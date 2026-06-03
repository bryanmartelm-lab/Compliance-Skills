# Changelog

All notable changes to the **kyb** plugin are recorded here. This project is actively maintained —
improvements ship in response to partner feedback.

The format is based on [Keep a Changelog](https://keepachangelog.com/). Versions follow
[Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-06-03
### Added
- Initial release of the `kyb` completeness reviewer plugin.
- `/kyb:review` command — reviews a folder or zip and writes a reviewer report (`.md`) + structured result (`.json`).
- `kyb-completeness-check` skill: 8-step claim-based review rulebook, output schema, and reviewer report template.
- Bundled `lessons/` folder (portable review judgment): proof-of-address attribute checks, sub-25% UBO surfacing, no-rationalizing.
- Safe zip extractor that preserves duplicate filenames.
