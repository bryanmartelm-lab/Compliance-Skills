#!/usr/bin/env python3
"""
validate_review.py -- Hard gate that a KYB review JSON must pass BEFORE the review is finalized.

Purpose: make the "eyeballed a Proof of Address and skipped the type check" failure
UNSHIPPABLE. Every proof_of_address claim (company + each UBO) must carry a `poa_check`
worksheet that records the document type, maps it to the closed allow-list, and quotes
the document's own masthead as evidence. The validator then enforces that the recorded
status is consistent with that worksheet -- and that the evidence quote does not contradict
the claimed type.

Exit code 0 = review may be finalized. Non-zero = DO NOT FINALIZE; fix the violations printed.

Usage:
    python validate_review.py kyb-reviews/<entity_slug>_<YYYY-MM-DD>.json
"""

import sys
import json
import re

# The closed allow-list. A PoA is valid ONLY if its actual document type is one of these.
ACCEPTED_TYPES = {"utility_bill", "bank_statement", "government_letter", "lease_tenancy"}
ALLOWED_ENUM = ACCEPTED_TYPES | {"NONE"}

# Tokens that, if present in the document's own masthead/title (evidence_quote), prove the
# document is NOT a proof of address -- regardless of what name/address it happens to show.
# This is the deterministic catch for "trade licence / certificate / invoice dressed up as PoA".
DISQUALIFYING_TOKENS = [
    "licence", "license",          # trade/commercial licence
    "certificate", "certidao", "certidão",
    "memorandum", "articles of association",
    "invoice", "fatura",
    "incorporation", "formation",
    "share register", "partners list", "shareholder",
    "trade name", "commercial register",
]

# A utility bill is legitimately titled "invoice" / "fatura" / "Tax Invoice" in most
# jurisdictions -- every Brazilian agua/luz/gas/internet bill says "Fatura" on its masthead.
# So an invoice-word alone must not disqualify a document that is BOTH classified
# utility_bill AND whose own masthead names a metered utility service. A commercial or
# virtual-office invoice names no such service, so it still fails the gate.
INVOICE_TOKENS = {"invoice", "fatura"}
UTILITY_SERVICE_TERMS = [
    "agua", "água", "water", "esgoto", "sewage", "saneamento",
    "electric", "eletric", "elétric", "energia", "luz",
    "gas", "gás", "internet", "banda larga", "broadband", "fibra",
]


def _disqualifying_hit(quote_lower, accepted):
    """First disqualifying token in the quote, or None. Excuses an invoice-word on a
    genuine utility bill (see INVOICE_TOKENS)."""
    for token in DISQUALIFYING_TOKENS:
        if token not in quote_lower:
            continue
        if (token in INVOICE_TOKENS
                and accepted == "utility_bill"
                and any(term in quote_lower for term in UTILITY_SERVICE_TERMS)):
            continue  # utility bill legitimately titled "fatura"/"invoice"
        return token
    return None


VALID_STATUSES = {"SUPPORTED", "PARTIAL", "NOT_SUPPORTED", "CONTRADICTED"}


def _err(violations, where, msg):
    violations.append(f"[{where}] {msg}")


def check_poa(poa, subject_kind, subject_label, violations):
    """subject_kind: 'company' or 'ubo'. Enforces the type-gate-first rule."""
    where = f"{subject_kind}:{subject_label}"
    status = poa.get("status")
    if status not in VALID_STATUSES:
        _err(violations, where, f"proof_of_address.status missing/invalid: {status!r}")

    chk = poa.get("poa_check")
    if not isinstance(chk, dict):
        _err(violations, where,
             "MISSING poa_check worksheet -- the document-type gate was not run. "
             "Add poa_check{evidence_quote, document_type, accepted_type, subject_name, "
             "address_shown, address_type, recency_status} before assigning a status.")
        return  # nothing else checkable

    quote = (chk.get("evidence_quote") or "").strip()
    doc_type = (chk.get("document_type") or "").strip()
    accepted = chk.get("accepted_type")
    addr_type = (chk.get("address_type") or "").strip().lower()
    recency = (chk.get("recency_status") or "").strip().lower()
    subj_name = (chk.get("subject_name") or "").strip()

    # Gate 1 must be recorded and grounded in a verbatim quote from the document.
    if not quote:
        _err(violations, where, "poa_check.evidence_quote empty -- quote the document's "
                                "own masthead/title (issuer + document name).")
    if not doc_type:
        _err(violations, where, "poa_check.document_type empty -- name what the document ACTUALLY is.")
    if accepted not in ALLOWED_ENUM:
        _err(violations, where,
             f"poa_check.accepted_type {accepted!r} not in {sorted(ALLOWED_ENUM)}.")

    # Evidence cross-check: a masthead that names a non-PoA document cannot be an accepted type.
    ql = quote.lower()
    hit = _disqualifying_hit(ql, accepted)
    if hit and accepted in ACCEPTED_TYPES:
        _err(violations, where,
             f"evidence_quote contains '{hit}' (document self-identifies as a non-PoA type) "
             f"but accepted_type is {accepted!r}. A document that says it is a "
             f"licence/certificate/invoice/etc. is NOT a proof of address -> accepted_type must be NONE.")

    # Type-gate-first: NONE means it fails outright, no matter the attributes.
    if accepted == "NONE" and status != "NOT_SUPPORTED":
        _err(violations, where,
             f"accepted_type=NONE (not on the allow-list) but status={status}. "
             f"A non-allow-list document MUST be NOT_SUPPORTED regardless of name/address/recency.")

    # If it is claimed SUPPORTED, every gate must be a clean pass.
    if status == "SUPPORTED":
        if accepted not in ACCEPTED_TYPES:
            _err(violations, where, f"status SUPPORTED but accepted_type={accepted!r} is not an allowed type.")
        if not subj_name:
            _err(violations, where, "status SUPPORTED but poa_check.subject_name is empty.")
        want_addr = "business" if subject_kind == "company" else "residential"
        if addr_type != want_addr:
            _err(violations, where,
                 f"status SUPPORTED but address_type={addr_type!r}; a {subject_kind} PoA requires "
                 f"a {want_addr} address.")
        if recency != "pass":
            _err(violations, where, f"status SUPPORTED but recency_status={recency!r} (must be 'pass').")


def main():
    if len(sys.argv) != 2:
        print("usage: python validate_review.py <review.json>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        review = json.load(f)

    violations = []

    # Company PoA -- pull from business_claims[claim == company_proof_of_address].
    company_poa = None
    for bc in review.get("business_claims", []):
        if bc.get("claim") == "company_proof_of_address":
            company_poa = bc
            break
    if company_poa is None:
        _err(violations, "company:_", "business_claims has no company_proof_of_address entry.")
    else:
        check_poa(company_poa, "company", "company", violations)

    # Each UBO PoA.
    ubos = review.get("ubo_claims", [])
    if not ubos:
        _err(violations, "ubo:_", "ubo_claims is empty -- at least one UBO required.")
    for ubo in ubos:
        name = ubo.get("name", "?")
        poa = ubo.get("proof_of_address")
        if not isinstance(poa, dict):
            _err(violations, f"ubo:{name}", "missing proof_of_address block.")
        else:
            check_poa(poa, "ubo", name, violations)

    if violations:
        print(f"REVIEW BLOCKED -- {len(violations)} PoA gate violation(s). DO NOT FINALIZE.\n")
        for v in violations:
            print("  - " + v)
        return 1

    print("OK -- all proof_of_address claims passed the type-gate worksheet. Safe to finalize.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
