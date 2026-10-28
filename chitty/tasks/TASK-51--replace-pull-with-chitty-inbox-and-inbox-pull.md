---
title: Replace pull with chitty inbox and inbox --pull
status: todo
created: 2026-10-28
---

## Description

pull consumes the inbox, with no way to see what is waiting first. chitty inbox lists waiting suggestions (origin, date, title) without changing anything; chitty inbox --pull imports them all, as pull does today. Selective pulls wait until there is a need to pull a single item.

## Acceptance Criteria

- [ ] chitty inbox lists waiting suggestions one per line with origin, date and title, supports --json, and changes nothing; when empty it says so on stderr with empty stdout
- [ ] When suggestions are waiting, chitty inbox ends with a hint to run chitty inbox --pull
- [ ] chitty inbox --pull behaves like today's pull
- [ ] pull still works but warns that it is deprecated in favour of chitty inbox --pull and suggests re-running chitty init to refresh the guide (other repos' guides still say chitty pull)
- [ ] The 'suggestions waiting' hint, the managed guide block, MCP tools (inbox list and pull, in inbox.py), README and PLAN.md all use the new command
- [ ] Tests cover listing, empty inbox, JSON, --pull and the deprecated alias

## Notes

Decided with the human: inbox --pull rather than two top-level commands; no selective pull yet. I added the pull alias so the guide in other repos keeps working until init refreshes it.

## History

- 2026-10-28 → todo
