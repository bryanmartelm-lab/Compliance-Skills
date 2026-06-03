# KYB Tools — Claude Code marketplace

A small marketplace containing the **`kyb`** plugin: a portable KYB (Know Your Business) document
completeness reviewer. Partners install it into their own Claude Code and run reviews locally —
**bring your own Claude**. There is no server, no Slack, and no data leaves your machine beyond the
documents you ask Claude to read.

> **Created & maintained by Bryan Martel.** This engine is actively maintained — the rulebook and the
> `lessons/` judgment are refined and shipped based on partner feedback. Authorship lives here in the
> repo (manifests + commit history + [CHANGELOG](./CHANGELOG.md)); it never appears in review output.

---

## What you need (the one prerequisite)

The reviewer *is* Claude — so you need **Claude Code installed and signed in** with any Claude plan
(Pro / Max / Team) or an Anthropic API key. The review runs on **your** Claude subscription, so each
review uses your own usage. Nothing is billed to the plugin author.

You also need **Python 3** on your PATH (used only to unzip document packages safely).

---

## Install (one time)

```
/plugin marketplace add bryanmartelm-lab/Compliance-Skills   # or a local path / git URL to this repo
/plugin install kyb@kyb-tools
```

> Installing from a local copy instead of GitHub? Point the marketplace at the folder:
> `/plugin marketplace add "C:/Bryan skills/kyb-review-plugin"`

Restart Claude Code if prompted. Confirm it's loaded:

```
/help        # you should see the /kyb:review command
```

---

## Run a review

Point it at a **folder** of documents or a **`.zip`**:

```
/kyb:review ./acme-corp-docs
/kyb:review ./packages/acme-kyb.zip
```

Claude will:
1. Extract the package (if it's a zip), handling duplicate filenames.
2. Read **every** document (content, not filenames; any language).
3. Apply the review rulebook + accumulated lessons.
4. Write two files into `./kyb-reviews/`:
   - `<entity>_<date>.json` — structured result (the source of truth)
   - `<entity>_<date>.md` — a reviewer report **plus** a copy-ready client request
5. Print a short summary in chat.

This is a **document completeness check only** — it does not approve onboarding or make a final
compliance decision.

---

## Customizing it for your team

- **Add review judgment:** drop a `*.md` file into
  `plugins/kyb/skills/kyb-completeness-check/lessons/`. The engine reads the whole folder every run,
  so your rule takes effect immediately. This is how the engine's institutional knowledge travels.
- **Change the report format:** edit `REPORT_TEMPLATE.md` in the same skill folder.
- **Change the rules / thresholds:** edit `SKILL.md` and `OUTPUT_SCHEMA.md`.

After editing, partners get updates by re-running `/plugin marketplace update kyb-tools`.

---

## What's inside

```
kyb-review-plugin/
├── .claude-plugin/marketplace.json     # marketplace manifest
└── plugins/kyb/
    ├── .claude-plugin/plugin.json      # plugin manifest
    ├── commands/review.md              # the /kyb:review entry point
    └── skills/kyb-completeness-check/
        ├── SKILL.md                    # the review rulebook (8-step process)
        ├── OUTPUT_SCHEMA.md            # JSON output contract
        ├── REPORT_TEMPLATE.md          # reviewer report + client request format
        ├── extract_kyb_package.py      # safe zip extractor
        └── lessons/                    # portable, accumulated review judgment
```
