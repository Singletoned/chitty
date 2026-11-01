---
title: Show an emoji for each status and flag
status: backlog
depends_on:
  - TASK-70
  - TASK-74
created: 2026-11-01
---

## Description

Words are slower to scan than symbols. `chitty list` and `show` should print a fixed emoji for each status, and for each flag once flags exist (for example `doing ⛔ Awaiting a product decision` for a blocked task). Files keep the words; emoji are display only. The mapping lives in one place in `model.py` so the CLI and MCP agree. Choose glyphs that render at one column in common terminals, and keep plain words available for `--json` and scripts.

## Notes

With the human: the queued emoji must read as blocked by another ticket, not just waiting. Candidates: 🔒 for queued (it unlocks by itself when the task in front finishes) and ⛔ for `blocked_by` (needs someone to act).

## History

- 2026-11-01 → backlog
