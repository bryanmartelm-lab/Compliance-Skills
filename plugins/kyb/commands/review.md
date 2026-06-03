---
description: Run a KYB document completeness review on a folder or zip. Usage:/kyb:review <path-to-folder-or-zip>
---

# /kyb:review — KYB Completeness Review

You are running a **KYB (Know Your Business) completeness review** on a set of documents the
user points you at. Follow this orchestration exactly.

The input path is: **$ARGUMENTS**

If `$ARGUMENTS` is empty, ask the user for the folder or zip to review (or default to the current
directory if they confirm), then continue.

---

## STEP 1 — Locate and extract the documents

- If the input path is a **`.zip`**, extract it first using the bundled extractor:
  ```bash
  python "${CLAUDE_PLUGIN_ROOT}/skills/kyb-completeness-check/extract_kyb_package.py" "<zip_path>" "<output_dir>"
  ```
  Use an output dir like `./kyb-reviews/_extracted/<entity_slug>/`. Note any DUPLICATE filename
  warnings the extractor prints — when duplicates exist you must read **all** copies.
- If the input path is a **folder**, use it directly.
- Build a list of every file to review (PDFs, images, txt, docx, etc.).

## STEP 2 — Load the review engine

Read these bundled files in full before judging anything:

1. `${CLAUDE_PLUGIN_ROOT}/skills/kyb-completeness-check/SKILL.md` — the review rulebook (8-step process)
2. `${CLAUDE_PLUGIN_ROOT}/skills/kyb-completeness-check/OUTPUT_SCHEMA.md` — the JSON output contract
3. `${CLAUDE_PLUGIN_ROOT}/skills/kyb-completeness-check/REPORT_TEMPLATE.md` — the report format
4. **Every** file in `${CLAUDE_PLUGIN_ROOT}/skills/kyb-completeness-check/lessons/` — accumulated
   review judgment. These are binding; apply them.

## STEP 3 — Read every document (content, not filename)

- Open and read EVERY file in the package. Never classify on filename alone — files are frequently
  mislabeled. For image/scanned files, inspect the visual content.
- Documents may be in any language; read the original and extract the underlying facts.

## STEP 4 — Run the review

- Execute the full 8-step review process from `SKILL.md`.
- Apply hard vs soft gating and subject-binding rules exactly. **Do not rationalize** around the
  rules (see lessons).
- Produce the structured result that conforms to `OUTPUT_SCHEMA.md` (this JSON is the source of truth).

## STEP 5 — Write the outputs

Create an output folder `./kyb-reviews/` if it does not exist, then write two files named
`<entity_slug>_<YYYY-MM-DD>`:

1. **`<entity_slug>_<YYYY-MM-DD>.json`** — the OUTPUT_SCHEMA JSON.
2. **`<entity_slug>_<YYYY-MM-DD>.md`** — the reviewer report, rendered from the JSON using
   `REPORT_TEMPLATE.md`.

Use today's date (run `date +%Y-%m-%d`). Derive `<entity_slug>` from the legal entity name
(lowercase, hyphenated).

## STEP 6 — Summarize in chat

Print a short summary to the reviewer:
- Outcome (FULL / PARTIAL / NO_GO) + access tier
- The 1–3 decision-driver bullets (`internal_summary`)
- Exact missing items, if any
- The paths to the two files you wrote

Then stop. This is a **document completeness check only** — you do not approve onboarding, grant
access, or make a final compliance decision.
