---
title: Let `chitty inbox --pull` import one suggestion
status: backlog
created: 2026-11-21
---

## Description

Asked for by the owner, 2026-11-20. `chitty inbox --pull` imports every waiting suggestion at once; nothing imports just one. On 2026-11-20 the owner wanted only the suggestion "Do not error a `todo` ticket whose branch already has work when the pre-session check fails" as a ticket, with about 17 others waiting. The agent had to create TASK-481 by hand with `chitty add -s backlog --note 'Suggestion origin: chitty'`, copying what `inbox.pull` does (`src/chitty/inbox.py`), and then delete the suggestion file from `~/.local/share/chitty/inbox/chitty/` so a later pull would not import it twice. That is hand-editing Chitty's own storage, and easy to get wrong.

Suggestion: give each waiting suggestion a short handle in `chitty inbox` and `chitty inbox --json` output, for example the hex ID already in its file name (`suggestion-<hex>.md`) or a prefix of it. Let `chitty inbox --pull <handle>` (repeatable) import only those, with the same status, origin note and claim-then-delete handling as a full pull. Keep plain `--pull` importing everything.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:56Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:57Z nimble-umber-gannet: changed notes
