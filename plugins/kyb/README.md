# kyb — KYB Completeness Reviewer (plugin)

Runs a KYB document completeness review on a local folder or zip and produces a reviewer report
plus structured JSON. Runs entirely on your own Claude — no external services.

## Command

```
/kyb:review <path-to-folder-or-zip>
```

## Requirements

- Claude Code, signed in (Pro / Max / Team or API key) — the review runs on your usage.
- Python 3 on PATH (zip extraction only).

## Outputs

Written to `./kyb-reviews/`:
- `<entity>_<date>.json` — OUTPUT_SCHEMA result (source of truth)
- `<entity>_<date>.md` — reviewer report + copy-ready client request

## Extend

Add review judgment by dropping a `*.md` into `skills/kyb-completeness-check/lessons/`.
Edit `skills/kyb-completeness-check/SKILL.md` to change the rules.

See the marketplace README for full install instructions.
