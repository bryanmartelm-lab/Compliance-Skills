# OUTPUT SCHEMA

This document defines the structured output of the KYB Completeness Review engine.

- Machine-readable
- Deterministic
- Directly mapped to the reviewer report (REPORT_TEMPLATE.md)
- No ambiguity or optional interpretation

---

# PURPOSE

The schema exists to ensure that the engine:

1. reads and evaluates document content
2. determines claim outcomes
3. produces a consistent structured result
4. maps cleanly into the reviewer report and the client-facing request

This schema is the output contract between:

- SKILL.md
- the execution engine
- REPORT_TEMPLATE.md

---

# CORE PRINCIPLES

- Every root field must always be present
- Use explicit values
- Do not omit keys
- Use empty arrays `[]` where applicable
- Use `null` only where explicitly allowed
- Do not include free text outside defined fields
- Do not duplicate the same issue across multiple fields unless the field serves a different purpose
- `UNKNOWN` must never appear in final output; it must be converted to `NOT_SUPPORTED` before output
- when a limitation is known, the output must state the actual reason rather than only `NOT_SUPPORTED`

---

# ROOT STRUCTURE

```json
{
  "review_outcome": "FULL | PARTIAL | NO_GO",
  "access_tier": "TIER_0 | TIER_1 | TIER_2",
  "controls": {
    "daily_cap": "number | 0 | null",
    "weekly_cap": "number | 0 | null",
    "monthly_cap": "number | 0 | null",
    "monitoring_level": "LEVEL_0 | LEVEL_1 | LEVEL_2 | LEVEL_3 | null"
  },
  "business_claims": [],
  "ubo_claims": [],
  "hard_failures": [],
  "soft_failures": [],
  "contradictions": [],
  "missing_items": {
    "company": [],
    "ubos": []
  },
  "internal_summary": []
}
```

---

# FIELD DEFINITIONS

## review_outcome

Final KYB result.

Allowed values:

- `FULL`
- `PARTIAL`
- `NO_GO`

Meaning:

- `FULL` → all required claims supported, no soft issues, no contradictions
- `PARTIAL` → no hard failures, but at least one partial/soft issue remains
- `NO_GO` → one or more hard-gating failures or contradictions

---

## access_tier

Operational access mapping derived from `review_outcome`.

Allowed values:

- `TIER_0`
- `TIER_1`
- `TIER_2`

Mapping:

- `NO_GO` → `TIER_0`
- `PARTIAL` → `TIER_1`
- `FULL` → `TIER_2`

---

## controls

Operational restrictions associated with the output.

### daily_cap / weekly_cap / monthly_cap

Allowed values:

- `number` → when restricted access applies
- `0` → when no access is permitted (`NO_GO`)
- `null` → when unrestricted access applies (`FULL`)

### monitoring_level

Allowed values:

- `LEVEL_0`
- `LEVEL_1`
- `LEVEL_2`
- `LEVEL_3`
- `null`

Meaning:

- `LEVEL_0` → standard monitoring
- `LEVEL_1` → slightly enhanced monitoring
- `LEVEL_2` → enhanced monitoring
- `LEVEL_3` → maximum monitoring
- `null` → no access / monitoring not applicable

Mapping:

- `FULL` → `LEVEL_0`
- `PARTIAL` → `LEVEL_1` / `LEVEL_2` / `LEVEL_3` as determined by restriction logic
- `NO_GO` → `null`

---

## business_claims

Array of claim objects for business-level claims.

Required business claims:

- `company_exists`
- `ownership_100`
- `ubo_identified`
- `directors_identified`
- `company_proof_of_address`
- `source_of_funds`

Structure:

```json
{
  "claim": "string",
  "status": "SUPPORTED | PARTIAL | NOT_SUPPORTED | CONTRADICTED",
  "evidence": ["string"],
  "gap": "string | null"
}
```

Field meanings:

- `claim` → normalized business claim name
- `status` → final claim result
- `evidence` → list of supporting file names / identifiers actually used
- `gap` → exact problem, or `null` if fully supported

Rules:

- Every required business claim must be included
- Status must be explicit
- If no evidence was used, `evidence` must be `[]`
- `gap` must explain why a claim is not supported, partial, or contradicted
- `evidence` must include only the files actually relied on for that claim
- `NOT_SUPPORTED` must be interpreted according to claim type:
  - hard-gated required claims may produce `NO_GO`
  - soft-gated required claims may produce `PARTIAL`
- the business claim `ubo_identified` confirms that UBOs have been identified at package level; it does not replace per-UBO validation in `ubo_claims`
- where a claim is not supported due to readability, language, format, or extraction limitations, the `gap` must state that reason explicitly

---

## ubo_claims

Array of per-UBO claim objects.

Structure:

```json
{
  "name": "string",
  "identity": {
    "status": "SUPPORTED | PARTIAL | NOT_SUPPORTED | CONTRADICTED",
    "evidence": ["string"],
    "gap": "string | null"
  },
  "link_to_company": {
    "status": "SUPPORTED | PARTIAL | NOT_SUPPORTED | CONTRADICTED",
    "evidence": ["string"],
    "gap": "string | null"
  },
  "proof_of_address": {
    "status": "SUPPORTED | PARTIAL | NOT_SUPPORTED | CONTRADICTED",
    "evidence": ["string"],
    "gap": "string | null",
    "poa_check": { "see PROOF OF ADDRESS WORKSHEET below — MANDATORY" }
  }
}
```

Rules:

- All identified UBOs must be listed
- At least one UBO must be listed
- Each UBO must include all three claim blocks
- No UBO may be omitted because they are fully supported
- `proof_of_address` is always required in this model
- each claim evidence list must include only the files actually relied on for that UBO claim
- where a UBO claim is not supported due to readability, language, format, or extraction limitations, the `gap` must state that reason explicitly

---

## PROOF OF ADDRESS WORKSHEET (poa_check) — MANDATORY

Every `proof_of_address` claim — the `company_proof_of_address` business claim AND each
UBO's `proof_of_address` — MUST carry a `poa_check` object. The status is DERIVED from this
worksheet; it may not be asserted without it. A review is invalid and must not be finalized
if any PoA is missing this block or its status contradicts it.

```json
{
  "evidence_quote": "verbatim masthead/title from the document (issuer + document name)",
  "document_type": "what the document ACTUALLY is, by content",
  "accepted_type": "utility_bill | bank_statement | government_letter | lease_tenancy | NONE",
  "subject_name": "name printed on the document",
  "address_shown": "address printed on the document (or 'ADDRESS NOT SHOWN')",
  "address_type": "business | residential | none",
  "recency_status": "pass | fail"
}
```

Gate order is enforced and non-negotiable:

1. **Gate 1 — TYPE FIRST.** Map `document_type` to `accepted_type` using the closed
   allow-list. Anything not a utility bill / bank statement / government letter / lease-tenancy
   is `accepted_type = NONE`. `evidence_quote` must ground this in the document's own words.
2. If `accepted_type = NONE` → `status` MUST be `NOT_SUPPORTED`, regardless of name/address/recency.
3. Only if Gate 1 passes do the attributes matter: a company PoA needs `address_type = business`,
   a UBO PoA needs `address_type = residential`, and `recency_status = pass`, for `status = SUPPORTED`.

A document whose `evidence_quote` self-identifies as a licence / certificate / invoice /
memorandum / register is NOT a proof of address — `accepted_type` must be `NONE`.

---

## hard_failures

List of strings representing all hard-gating issues that caused or justify `NO_GO`.

Examples:

- `UBO proof of address missing for John Smith`
- `Ownership not fully evidenced`
- `Certificate of Incorporation missing`
- `Ownership contradiction: John Smith 100% vs Anna White 100%`

Rules:

- If `hard_failures` is non-empty → `review_outcome` must be `NO_GO`
- If none → `[]`

---

## soft_failures

List of strings representing non-hard issues that justify `PARTIAL`.

Examples:

- `Company proof of address missing`
- `Company proof of address outdated (>90 days)`
- `Corporate documents outdated (>6 months)`
- `Source of funds missing`

Rules:

- If `soft_failures` is non-empty and `hard_failures` is empty → output may be `PARTIAL`
- If none → `[]`

---

## contradictions

List of strings representing actual evidentiary conflicts.

Examples:

- `Conflicting ownership: John Smith 100% vs Anna White 100%`
- `Conflicting address information across corporate documents`
- `Conflicting UBO identity information`

Rules:

- Contradictions must be explicit
- Contradictions must not be downgraded into generic missing items
- a contradiction recorded in `contradictions` must correspond to at least one claim status marked `CONTRADICTED`
- If `contradictions` is non-empty → result must be `NO_GO`
- If none → `[]`

---

## missing_items

Exact items that must be requested.

Structure:

```json
{
  "company": ["string"],
  "ubos": [
    {
      "name": "string",
      "items": ["string"]
    }
  ]
}
```

### company

List of exact missing or replacement company-level items.

Examples:

- `Certificate of Incorporation`
- `Company proof of address dated within the last 90 days`
- `Source of funds documentation`
- `Clarified ownership structure accounting for 100% ownership`

### ubos

List of per-UBO missing items.

Rules:

- All UBOs must appear
- If a UBO has no missing items, `items` must be `[]`
- Do not omit a UBO just because nothing is missing for them

Example:

```json
{
  "name": "John Smith",
  "items": []
}
```

or

```json
{
  "name": "Maria Lopez",
  "items": [
    "Proof of address in UBO name dated within the last 90 days"
  ]
}
```

---

## internal_summary

Array of short factual summary points.

Rules:

- Maximum 3 items
- Factual only
- Must reflect decision drivers
- No generic or process language
- No client-facing tone

Good examples:

- `UBO identity and ownership verified`
- `Company proof of address missing`
- `Source of funds missing`

Bad examples:

- `Review completed`
- `Checks performed`
- `Documents analyzed`

---

# DERIVATION RULES (CRITICAL)

These rules are mandatory.

## 1. HARD OVERRIDE

If `hard_failures` is not empty:

- `review_outcome = NO_GO`
- `access_tier = TIER_0`
- `controls.daily_cap = 0`
- `controls.weekly_cap = 0`
- `controls.monthly_cap = 0`
- `controls.monitoring_level = null`

## 2. CONTRADICTION OVERRIDE

If `contradictions` is not empty:

- contradiction must also be reflected in hard-failure logic
- `review_outcome = NO_GO`

## 3. CLAIM-TYPE MAPPING RULE

A required claim with status `NOT_SUPPORTED` must be mapped according to claim type:

- hard-gated required claims → must be reflected in `hard_failures`
- soft-gated required claims → may be reflected in `soft_failures`

## 4. PARTIAL OUTCOME

If:

- `hard_failures` is empty
- `contradictions` is empty
- and either:
  - `soft_failures` is not empty
  - or any required business or UBO claim status is `PARTIAL`
  - or any required soft-gated claim status is `NOT_SUPPORTED`

Then:

- `review_outcome = PARTIAL`
- `access_tier = TIER_1`

## 5. FULL OUTCOME

Only if all of the following are true:

- `hard_failures` is empty
- `soft_failures` is empty
- `contradictions` is empty
- all required business claims are `SUPPORTED`
- all required UBO claims are `SUPPORTED`

Then:

- `review_outcome = FULL`
- `access_tier = TIER_2`
- `controls.daily_cap = null`
- `controls.weekly_cap = null`
- `controls.monthly_cap = null`
- `controls.monitoring_level = LEVEL_0`

## 6. UNKNOWN HANDLING

`UNKNOWN` must never appear in final output.

Before output:

- `UNKNOWN → NOT_SUPPORTED`

## 7. SOFT GATING SUBSET RULE

Soft-gating conditions are a subset of `PARTIAL` outcomes.

Typical soft-gating examples:

- company proof of address issues
- corporate document recency issues
- source of funds missing/incomplete

## 8. PARTIAL PRECEDENCE RULE

Evaluation order must be:

1. `NO_GO` via hard gating / contradictions
2. `PARTIAL`
3. `FULL`

This order must be enforced in implementation.

---

# CONTROL MAPPING RULES

These values must be derived consistently.

## NO_GO

```json
{
  "access_tier": "TIER_0",
  "controls": {
    "daily_cap": 0,
    "weekly_cap": 0,
    "monthly_cap": 0,
    "monitoring_level": null
  }
}
```

## PARTIAL

If only company proof of address is missing:

```json
{
  "daily_cap": 2000,
  "weekly_cap": 5000,
  "monthly_cap": 10000,
  "monitoring_level": "LEVEL_1"
}
```

If source of funds is missing:

```json
{
  "daily_cap": 1000,
  "weekly_cap": 2500,
  "monthly_cap": 5000,
  "monitoring_level": "LEVEL_2"
}
```

If both company proof of address and source of funds are missing:

```json
{
  "daily_cap": 500,
  "weekly_cap": 2500,
  "monthly_cap": 5000,
  "monitoring_level": "LEVEL_2"
}
```

If multiple soft issues apply:

- enforce the most restrictive caps
- enforce the highest required monitoring level

## FULL

```json
{
  "access_tier": "TIER_2",
  "controls": {
    "daily_cap": null,
    "weekly_cap": null,
    "monthly_cap": null,
    "monitoring_level": "LEVEL_0"
  }
}
```

---

# EXAMPLE — PARTIAL

```json
{
  "review_outcome": "PARTIAL",
  "access_tier": "TIER_1",
  "controls": {
    "daily_cap": 500,
    "weekly_cap": 2500,
    "monthly_cap": 5000,
    "monitoring_level": "LEVEL_2"
  },
  "business_claims": [
    {
      "claim": "company_exists",
      "status": "SUPPORTED",
      "evidence": ["certificate_of_incorporation.pdf"],
      "gap": null
    },
    {
      "claim": "ownership_100",
      "status": "SUPPORTED",
      "evidence": ["shareholder_register.pdf"],
      "gap": null
    },
    {
      "claim": "ubo_identified",
      "status": "SUPPORTED",
      "evidence": ["shareholder_register.pdf"],
      "gap": null
    },
    {
      "claim": "directors_identified",
      "status": "SUPPORTED",
      "evidence": ["director_structure.pdf"],
      "gap": null
    },
    {
      "claim": "company_proof_of_address",
      "status": "NOT_SUPPORTED",
      "evidence": [],
      "gap": "Company proof of address missing"
    },
    {
      "claim": "source_of_funds",
      "status": "NOT_SUPPORTED",
      "evidence": [],
      "gap": "Source of funds not provided"
    }
  ],
  "ubo_claims": [
    {
      "name": "John Smith",
      "identity": {
        "status": "SUPPORTED",
        "evidence": ["john_smith_passport.pdf"],
        "gap": null
      },
      "link_to_company": {
        "status": "SUPPORTED",
        "evidence": ["shareholder_register.pdf"],
        "gap": null
      },
      "proof_of_address": {
        "status": "SUPPORTED",
        "evidence": ["john_smith_bank_statement.pdf"],
        "gap": null
      }
    }
  ],
  "hard_failures": [],
  "soft_failures": [
    "Company proof of address missing",
    "Source of funds missing"
  ],
  "contradictions": [],
  "missing_items": {
    "company": [
      "Company proof of address dated within the last 90 days",
      "Source of funds documentation"
    ],
    "ubos": [
      {
        "name": "John Smith",
        "items": []
      }
    ]
  },
  "internal_summary": [
    "UBO fully verified",
    "Company proof of address missing",
    "Source of funds missing"
  ]
}
```

---

# EXAMPLE — NO_GO

```json
{
  "review_outcome": "NO_GO",
  "access_tier": "TIER_0",
  "controls": {
    "daily_cap": 0,
    "weekly_cap": 0,
    "monthly_cap": 0,
    "monitoring_level": null
  },
  "business_claims": [
    {
      "claim": "company_exists",
      "status": "SUPPORTED",
      "evidence": ["certificate_of_incorporation.pdf"],
      "gap": null
    },
    {
      "claim": "ownership_100",
      "status": "CONTRADICTED",
      "evidence": ["ownership_chart_v1.pdf", "ownership_chart_v2.pdf"],
      "gap": "Conflicting ownership information"
    },
    {
      "claim": "ubo_identified",
      "status": "CONTRADICTED",
      "evidence": ["ownership_chart_v1.pdf", "ownership_chart_v2.pdf"],
      "gap": "Conflicting UBO information"
    },
    {
      "claim": "directors_identified",
      "status": "SUPPORTED",
      "evidence": ["director_structure.pdf"],
      "gap": null
    },
    {
      "claim": "company_proof_of_address",
      "status": "SUPPORTED",
      "evidence": ["company_bank_statement.pdf"],
      "gap": null
    },
    {
      "claim": "source_of_funds",
      "status": "SUPPORTED",
      "evidence": ["company_bank_statement.pdf"],
      "gap": null
    }
  ],
  "ubo_claims": [
    {
      "name": "John Smith",
      "identity": {
        "status": "SUPPORTED",
        "evidence": ["john_passport.pdf"],
        "gap": null
      },
      "link_to_company": {
        "status": "CONTRADICTED",
        "evidence": ["ownership_chart_v1.pdf", "ownership_chart_v2.pdf"],
        "gap": "Ownership information conflicts across documents"
      },
      "proof_of_address": {
        "status": "SUPPORTED",
        "evidence": ["john_bank_statement.pdf"],
        "gap": null
      }
    }
  ],
  "hard_failures": [
    "Ownership contradiction prevents confirmation of beneficial ownership"
  ],
  "soft_failures": [],
  "contradictions": [
    "John Smith listed as 100% owner in one document and Anna White listed as 100% owner in another"
  ],
  "missing_items": {
    "company": [
      "Clarified and consistent ownership structure documentation accounting for 100% ownership"
    ],
    "ubos": [
      {
        "name": "John Smith",
        "items": []
      }
    ]
  },
  "internal_summary": [
    "Ownership structure inconsistent",
    "Conflicting UBO information identified",
    "Beneficial ownership cannot be confirmed"
  ]
}
```

---

# HARD CONSTRAINTS

Never:

- omit required root fields
- include `UNKNOWN` in final output
- use free text outside defined fields
- mix internal and client-facing language
- omit UBOs from `missing_items.ubos`

Always:

- use explicit values
- preserve derivation logic
- ensure structured output matches KYB decision logic exactly
