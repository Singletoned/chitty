---
title: Show status glyphs, and why `chitty next` skips a ticket, in `chitty list`
status: backlog
priority: high
created: 2026-11-01
---

## Description

The human wants `chitty list` to tell a person accurately what the queue is doing. On 2026-11-06 it listed seven `todo` tickets while `chitty next --mode work` said `no next ticket`: three were owned by `human` and the rest waited on unfinished dependencies, and the list showed neither. Words are also slower to scan than symbols.

Rescoped by the human on 2026-11-06: this no longer waits for `TASK-70` or `TASK-74`. When those add `queued` or `blocked_by`, they give them glyphs in the same mapping.

Two changes to the human-readable `chitty list` output in `src/chitty/cli.py`; `--json` keeps its words.

1. Each row shows a fixed glyph for its status before the status word, from one mapping in `src/chitty/model.py`: `backlog` 💤, `todo` 📋, `doing` 🔨, `review` 👀, `blocked` ⛔, `done` ✅. Keep the status word, so the columns still sort and grep. Emoji are two columns wide in most terminals, so align the columns by display width, not `len`.
2. A `todo`, `doing` or `review` ticket that `chitty next` would never select says why, at the end of its row: `🔒 waits on TASK-190, TASK-191` for unfinished dependencies, naming only the ones that are not yet done, and `👤 human` for owner `human`. The reason must come from the same code `next_action` uses, so the two cannot disagree: change `_ticket_action` in `src/chitty/store.py` (its `refuse=True` path already builds these messages) so a caller can get the reason without a `ChittyError`, rather than writing the rules again in the CLI. A ticket with no reason shown is one `chitty next` could select. `--json` gains a `skipped` field holding the reason, or `null`.

`TASK-197` (in `doing`) adds owners other than `human` that `chitty next` skips at `todo` and `doing`, and `TASK-186`'s modes exist already; whichever of this ticket and `TASK-197` lands second shows its owner reason the same way, as `👤 <owner>`. Out of scope: `chitty show`, the MCP `list` tool's output beyond the shared `skipped` field, and run locks.

## Acceptance Criteria

- [ ] Tests show each status's glyph in `chitty list` with the columns aligned, and `--json` unchanged apart from `skipped`
- [ ] Tests show a ticket waiting on an unfinished dependency and one owned by `human` marked with their reasons, a ticket with a finished dependency unmarked, and every unmarked `todo`, `doing` or `review` ticket being one `chitty next` can select
- [ ] `README.md` and `PLAN.md` describe the glyphs and the reasons

## Notes

With the human: the queued emoji must read as blocked by another ticket, not just waiting. Candidates: 🔒 for queued (it unlocks by itself when the task in front finishes) and ⛔ for `blocked_by` (needs someone to act).

## History

- 2026-11-01 → backlog
- 2026-11-06T09:26:17Z youthful-toad: changed title, priority, dependencies, description, acceptance criteria
