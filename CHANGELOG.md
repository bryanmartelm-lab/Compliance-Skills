# Changelog

All notable changes to the **kyb** plugin are recorded here. This project is actively maintained —
improvements ship in response to partner feedback.

The format is based on [Keep a Changelog](https://keepachangelog.com/). Versions follow
[Semantic Versioning](https://semver.org/).

## [0.4.0] — 2026-11-04
### Added
- **One document ≠ multiple claims**: the claim chain runs separately per claim even when claims
  share a file. A formation deed / articles evidences the position at incorporation only; current
  ownership and directorship need a current registry extract or register of members.
- **Documented vs inferred ownership split**: an inferred "100%" stays a hard failure; a fully
  documented split whose only unnamed holder is below 25% is a soft gap (PARTIAL), with no KYC on
  that holder.
- **UK HMRC UTR document** required for UK limited companies (soft gap if missing), alongside the
  actual Articles of Association.
- **Source of Funds — assessing bank statements**: client flow on payments / MSB / on-ramp accounts
  is turnover, not revenue; ask for invoices reconciling to credits with both legs, and chase
  self-funding credits. UBO personal accounts leave scope once the company itself trades, subject
  to proportionality and data minimisation.

### Changed
- SOFT GATING list now names missing tax-reference documents and a sub-25% unnamed holder.

## [0.3.0] — 2026-10-27
### Added
- **Constitutional documents always requested**: articles / memorandum / operating agreement,
  named per jurisdiction and company type (lookup table included). Not ownership evidence, and
  ownership evidence does not replace it. Absence is a soft gap → PARTIAL.
- **Financial statements always requested, note-only**: balance sheet, income statement, or P&L.
  Never gates the outcome; surfaced via the new `notes` field and in `missing_items.company`.
- **`notes` field** in the output schema for non-gating items, plus a Notes section in the
  reviewer report and standard client wording for financials (including on FULL outcomes).
- **Internet bills accepted as proof of address**: a home internet bill (in the individual's
  name) or an office internet bill (in the company's name) counts as a utility bill. Mobile
  subscriptions are not accepted.
- **`validate_review.py`**: blocks a review whose proof-of-address claims skip or contradict the
  `poa_check` type-gate worksheet; `/kyb:review` runs it before rendering the report.
- **`kyb-document-reviewer` agent**: optional document-reader subagent for large packages,
  returning a per-claim evidence log for the orchestrator to verify.

## [0.2.0] — 2026-07-09
### Added
- **Identity capture-medium gate**: identity documents are accepted only as an original
  photograph — scans, photocopies, and screenshots are NOT_SUPPORTED regardless of legibility,
  checked before name/DOB.
- **US Tax IDs section**: EIN (company) and SSN/ITIN (US-resident UBO) required as tax/identity
  evidence, explicitly separated from ownership evidence (EIN "responsible party" ≠ owner; US LLC
  ownership needs operating agreement + member register/certificates, K-1 for multi-member).
- **Document-type verification** rules: certificate of incorporation vs M&A/formation deed, UAE
  free-zone dual-document requirement, invoice (incl. Regus/virtual-office) is not a valid PoA,
  and self-certified ownership charts / holding-company look-through.
- **Mandatory `poa_check` worksheet** in the output schema: every proof of address must record the
  document's actual type against a closed allow-list (type-first gate) with a verbatim masthead quote.
- **Delegation guidance**: subagents may read documents only when equipped with the rulebook,
  returning a per-claim evidence log, with the orchestrator independently verifying decision-critical
  documents before any FULL/PARTIAL.

## [0.1.0] — 2026-06-03
### Added
- Initial release of the `kyb` completeness reviewer plugin.
- `/kyb:review` command — reviews a folder or zip and writes a reviewer report (`.md`) + structured result (`.json`).
- `kyb-completeness-check` skill: 8-step claim-based review rulebook, output schema, and reviewer report template.
- Bundled `lessons/` folder (portable review judgment): proof-of-address attribute checks, sub-25% UBO surfacing, no-rationalizing.
- Safe zip extractor that preserves duplicate filenames.
