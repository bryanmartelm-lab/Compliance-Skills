# Lessons — portable review judgment

These files are the accumulated judgment of the KYB review engine. They travel *inside* the plugin
(unlike Claude Code's user-scoped auto-memory, which does not), so every partner who installs the
plugin inherits them automatically.

**The review process (`SKILL.md`) reads every file in this folder before judging.** Treat each
lesson as a binding rule, not a suggestion.

## How to add your own lesson

Drop a new `my-rule.md` file in this folder. Keep it focused on a single review-judgment point,
state the rule plainly, and include a concrete failure case if you have one. No index file is
required — `SKILL.md` reads the whole folder.

## Current lessons

- `no-rationalizing.md` — follow the rulebook exactly; don't invent exceptions
- `poa-verify-all-attributes.md` — proof of address must satisfy all three attributes from the document itself
- `ubo-below-25-threshold.md` — surface "no shareholder ≥25%" explicitly
