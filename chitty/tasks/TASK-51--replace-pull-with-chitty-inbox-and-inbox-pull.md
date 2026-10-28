---
title: Replace pull with chitty inbox and inbox --pull
status: doing
created: 2026-10-28
---

## Description

pull consumes the inbox, with no way to see what is waiting first. chitty inbox lists waiting suggestions (origin, date, title) without changing anything; chitty inbox --pull imports them all, as pull does today. Selective pulls wait until there is a need to pull a single item.

## Acceptance Criteria

- [ ] chitty inbox lists waiting suggestions one per line with origin, date and title, supports --json, and changes nothing; when empty it says so on stderr with empty stdout
- [ ] When suggestions are waiting, chitty inbox ends with a hint to run chitty inbox --pull
- [ ] chitty inbox --pull behaves like today's pull
- [ ] The 'suggestions waiting' hint, the managed guide block, MCP tools (inbox list and pull, in inbox.py), README and PLAN.md all use the new command
- [ ] pull imports nothing and changes nothing; it exits non-zero with a message telling the user to run chitty inbox --pull and to re-run chitty init to refresh the guide
- [ ] Tests cover listing, empty inbox, JSON, --pull and that pull leaves the inbox untouched

## Plan

Trace inbox listing and pull behavior through CLI, MCP and guide documentation. Add a read-only `inbox` listing with JSON and an explicit `--pull`, convert `pull` to a failing migration hint, update callers and tests, then run `make check` and hand off for review.

## Notes

Decided with the human: inbox --pull rather than two top-level commands; no selective pull yet. I added the pull alias so the guide in other repos keeps working until init refreshes it.

Changed by the human: pull no longer works as an alias; it only explains what to run instead.

Implemented the read-only inbox listing and migration behavior; remaining work is MCP exposure, documentation inventory updates, version refresh, and focused coverage.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
