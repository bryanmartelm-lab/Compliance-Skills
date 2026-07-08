# Changelog

All notable changes to the **kyb** plugin are recorded here. This project is actively maintained —
improvements ship in response to partner feedback.

The format is based on [Keep a Changelog](https://keepachangelog.com/). Versions follow
[Semantic Versioning](https://semver.org/).

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
