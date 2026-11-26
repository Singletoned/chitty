---
title: "Planning guide: let tickets with fully specified dependency contracts go to todo"
status: backlog
created: 2026-11-26
provisional: true
---

## Description

The planning guide (`chitty guide plan`) says: 'If a ticket relies on a contract an unfinished ticket is building, keep it in planning with a note naming that ticket and re-check once it lands (depends_on alone is enough for plain ordering).' In echonomicon on 2026-11-25 this left about a dozen fully planned and cold-read tickets (TASK-134, 136, 222, 223, 224, 231, 232, 233, 245 and others) parked in planning, each needing a second planning pass after its dependency landed. Yet the dependency tickets pinned every name, signature and file format, depends_on already stops the runner starting them early, and any drift shows up as an immediate import error the worker can fix or bounce. The owner asked why they could not just go to todo. Suggested rewrite: 'A ticket may go to todo with depends_on alone when the dependency ticket fully specifies the contract it relies on (names, signatures, formats). Keep it in planning only while that contract is still vague; then note which ticket must settle it.' Cold reads do not need the dependency built.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-26T10:54:38Z calm-ochre-quail → backlog
- 2026-11-26T10:54:40Z calm-ochre-quail: changed notes
