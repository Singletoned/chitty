---
title: Show status glyphs, and why `chitty next` skips a ticket, in `chitty list`
status: doing
priority: high
created: 2026-11-01
---

## Description

The human wants `chitty list` to tell a person accurately what the queue is doing. On 2026-11-06 it listed several `todo` tickets while `chitty next --mode work` said `no next ticket`: some were owned by `human` and the rest waited on unfinished dependencies, and the list showed neither. Words are also slower to scan than symbols.

Rescoped by the human on 2026-11-06: this no longer waits for `TASK-70` or `TASK-74`. When those add `queued` or `blocked_by`, they give them glyphs in the same mapping. The older note below about 🔒 and ⛔ is superseded by this description.

Two changes to the human-readable `chitty list` output (`list_` in `src/chitty/cli.py`); `--json` keeps its words.

1. Each row shows a fixed glyph for its status before the status word, from one mapping in `src/chitty/model.py`: `backlog` 💤, `todo` 📋, `doing` 🔨, `review` 👀, `blocked` ⛔, `done` ✅. Keep the status word, so rows still grep. Every glyph is two columns wide, so plain padding keeps the columns aligned; pad the status word to the longest status (`backlog`, `blocked`: 7 characters), which also fixes today's misalignment of `blocked`.
2. A ticket that `chitty next` skips says why, at the very end of its row after any labels and branch: `👤 human` for owner `human` or a ticket in the `human` context, `🔒 waits on TASK-190, TASK-191` for a `todo` ticket with unfinished dependencies (only those not done, judged by `_dependency_is_done` exactly as `chitty next` judges them, which looks at `main`), and `⚠️ <message>` when a dependency reference is broken, so one bad ticket cannot make `chitty list` fail. `doing` and `review` tickets ignore dependencies in `chitty next` (`PLAN.md`, "Next action and runner"), so they never get 🔒. Rows for `backlog`, `blocked` and `done` get no reason: their status already says it. When several reasons apply, show the first one `chitty next` checks.

The reason must come from the same code as `next_action`, so the two cannot disagree. Split `_ticket_action` in `src/chitty/store.py` into a public `skip_reason(repo, stored) -> str | None`, holding the rules and returning the text above, and the part that builds the `NextAction`. `next_action` skips a ticket with a reason; `ticket_action` (the `--ticket` path) keeps its current `ChittyError` messages, which existing tests check. A ticket with no reason shown is one `chitty next` could select. The CLI `list --json` and the MCP `list` tool in `src/chitty/mcp.py` each add a `skipped` field, the reason or `null`; do not put it in `StoredTask.as_dict`, which `show`, `add` and `edit` also use.

`TASK-197` (in `doing`) adds owners other than `human` that `chitty next` skips at `todo` and `doing`; whichever of the two lands second makes that rule return `👤 <owner>` from `skip_reason`. Update the `CLI` and "Next action and runner" sections of `PLAN.md`, and the `chitty list` paragraph in `README.md`. Out of scope: `chitty show`, colour, and run locks (`TASK-200`).

## Acceptance Criteria

- [ ] `README.md` and `PLAN.md` describe the glyphs and the reasons
- [ ] Tests show each status's glyph in `chitty list` with the columns aligned, and `--json` and the MCP `list` tool unchanged apart from `skipped`
- [ ] Tests show a `todo` ticket waiting on an unfinished dependency, one owned by `human` and one with a broken dependency marked with their reasons, a `todo` ticket with a finished dependency and a `doing` ticket with an unfinished one unmarked, and every unmarked `todo`, `doing` or `review` ticket being one `chitty next` can select

## Plan

Inspect existing list/next/store/MCP behavior and tests, add a shared skip_reason plus status glyph rendering and JSON skipped fields, update documentation, then run the focused regression tests and full make check.

## Notes

With the human: the queued emoji must read as blocked by another ticket, not just waiting. Candidates: 🔒 for queued (it unlocks by itself when the task in front finishes) and ⛔ for `blocked_by` (needs someone to act).

Cold read by a fresh Sonnet subagent, 2026-11-06. Fixed: the shape of the refactor (`skip_reason` plus unchanged `ticket_action` errors), that dependency reasons use `_dependency_is_done` on `main`, alignment by fixed two-column glyphs and a seven-character status, where the reason goes, no reason for `backlog`/`blocked`/`done`, the first reason winning, `skipped` only in the two list outputs, the `human` context, broken dependencies shown not raised, 🔒 only on `todo` because `doing` and `review` ignore dependencies, and which doc sections change. Rejected: none.

## History

- 2026-11-01 → backlog
- 2026-11-06T09:26:17Z youthful-toad: changed title, priority, dependencies, description, acceptance criteria
- 2026-11-06T09:29:01Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T09:31:13Z youthful-toad backlog → todo
- 2026-11-06T16:33:27Z calm-ibis todo → doing
- 2026-11-06T16:33:39Z calm-ibis: wrote the plan
