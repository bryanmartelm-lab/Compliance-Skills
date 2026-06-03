# Surface "no shareholder ≥25%" explicitly

When the ownership structure shows that NO shareholder reaches the ≥25% UBO threshold (e.g.,
5 members × 20%, 6 × ~16.67%, equal-split structures), this fact must be surfaced explicitly in the
outcome.

Where to surface it:
- The reviewer report Summary line — e.g. "5 members at 20% each — no shareholder reaches the 25% UBO threshold"
- `internal_summary` in the OUTPUT_SCHEMA JSON — one of the (max 3) bullets must call out the sub-threshold split

Why it matters: compliance needs to see at a glance that beneficial ownership cannot be determined
by the standard ≥25% test and must fall back on control persons / senior managing officials. Saying
"5 members at 20% each" alone is not enough — the implication must be stated.

Applies whenever the Register of Members / corporate structure shows no single holder ≥25%,
regardless of overall outcome (FULL / PARTIAL / NO_GO).
