# REPORT TEMPLATE (REVIEWER-FACING)

This defines the markdown report rendered from the OUTPUT_SCHEMA JSON for the **reviewer**.
It replaces the Slack/UI delivery layer — there is no Slack, no channel routing, no merchant map.

Two audiences live in one file:
- **Part A — Reviewer report**: full internal detail (claims, gating, controls). For the person running the review.
- **Part B — Client-ready request**: a plain-language block the reviewer can copy and send to the business customer. No internal labels.

Render both parts. Map every field directly from the JSON — never invent data.

---

# STATUS ICONS

- FULL → ✅
- PARTIAL → 🟡
- NO_GO → 🔴

---

# PART A — REVIEWER REPORT (use this structure)

```
# [ICON] [ENTITY_NAME] ([CONTACT_NAME]) — [REVIEW_OUTCOME]

Reviewed: [YYYY-MM-DD]
Jurisdiction: [JURISDICTION or "—"]

## Summary
- [internal_summary[0]]
- [internal_summary[1]]
- [internal_summary[2]]

## Access
- Tier: [access_tier]
- Daily cap: [controls.daily_cap or "N/A"]
- Weekly cap: [controls.weekly_cap or "N/A"]
- Monthly cap: [controls.monthly_cap or "N/A"]
- Monitoring: [controls.monitoring_level or "N/A"]

## Business Claims
| Claim | Status | Evidence | Gap |
|-------|--------|----------|-----|
| company_exists | [status] | [evidence joined] | [gap or "—"] |
| ownership_100 | ... | ... | ... |
| ubo_identified | ... | ... | ... |
| directors_identified | ... | ... | ... |
| company_proof_of_address | ... | ... | ... |
| source_of_funds | ... | ... | ... |

## UBO Claims
For each UBO in ubo_claims:

### [UBO name]
- Identity: [status] — [evidence] — [gap or "—"]
- Link to company: [status] — [evidence] — [gap or "—"]
- Proof of address: [status] — [evidence] — [gap or "—"]

## Hard Failures
- [item] / None

## Soft Failures
- [item] / None

## Contradictions
- [item] / None

## Missing Items
**Company**
- [item] / None

**UBOs**
- [UBO name]: [item, item] / None
- ... (one line per UBO — never a global None when UBOs exist)

## Next Action
- FULL → Proceed with full activation
- PARTIAL → Maintain restricted access and request the missing documents
- NO_GO → Block onboarding and request the required hard-gating documents
```

Rules for Part A:
- All sections always present, even when the value is None.
- Summary: max 3 bullets, decision-drivers only — no "review completed" filler.
- Every missing item must correspond to a failure listed above it.
- List ALL identified UBOs individually; at least one UBO line must appear.

---

# PART B — CLIENT-READY REQUEST (copy/paste to the business customer)

Append this after a `---` divider. It is plain language with NO internal labels
(never expose FULL/PARTIAL/NO_GO, "hard/soft failure", "contradiction", tiers, or caps).

## FULL

```
**[ENTITY_NAME]** ([CONTACT_NAME]) — 🟢 Fully Activated

All required documents have been received. No further action is needed from your side at this stage.

_This is a document completeness check only. Final compliance review is still pending._
```

## PARTIAL

```
**[ENTITY_NAME]** ([CONTACT_NAME]) — 🟡 Activated with Restricted Access

The account is active with restricted access.

*To unlock full access, please send:*

**[Document name]**
- [plain-language explanation of what is missing/wrong, if useful]
- [exact document or correction required]
- [date / subject / format requirement, where relevant]

Once received, we'll review the documents and update your account status.

_This is a document completeness check only. Final compliance review is still pending._
```

## NO_GO

```
**[ENTITY_NAME]** ([CONTACT_NAME]) — 🔴 Additional Information Required

We need a few additional documents before we can continue onboarding.

*To continue your onboarding, please send:*

**[Document name]**
- [exact document required]
- [must be in the correct name / dated within the required period, where relevant]

Once received, we'll review the documents and continue your onboarding.

_This is a document completeness check only. Final compliance review is still pending._
```

## Client request patterns (use the closest fit per missing item)

- **Missing** → "please send [exact document]" + "[date/subject/format requirement]"
- **Wrong subject / wrong name** → "the document provided appears to be in a different name" + "please send [document] in the correct name"
- **Outdated** → "the document provided is outdated" + "please send an updated version dated within [period]"
- **Unreadable** → "the document provided could not be reviewed clearly" + "please resend a clear, complete version"

Client-request constraints:
- Specific, short, supportive. Bullets, not email prose. No greetings, no "if you have questions".
- Must match `missing_items` from the JSON. Never promise approval.
- Build the request blocks ONLY from `missing_items` (company + per UBO).
