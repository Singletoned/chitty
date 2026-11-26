---
title: Renumbering jumps to TASK-10000 because an archived ticket mentions `TASK-9999`
status: backlog
created: 2026-11-26
provisional: true
---

## Description

Seen 2026-11-25: `chitty renumber` on `main` gave provisional tickets `TASK-10000` onwards (first in commit `5967db80`, again for the 2026-11-25 inbox triage, up to `TASK-10024`), though the highest real ticket was `TASK-692`. Cause: `_plan_provisional_renumbering` in `src/chitty/store.py` reserves every ID mentioned in any ticket file's text (`_reserve_numbers` over `ids.ticket_references(path.read_text(), ...)`), and the archived `chitty/tasks/archive/TASK-443--chitty-run-with-the-pi-extension-flag-exits-0-doing-nothing.md` mentions a placeholder `TASK-9999`. `ids.next_number` is `max(used) + 1`, so one placeholder mention moves every later ID. Suggest: reserve mentioned numbers without letting them raise the maximum (allocate the lowest unused number above the highest real ticket, skipping mentioned ones), or reserve only mentions of IDs that a file or ref actually had. Decide whether to renumber `TASK-10000`-`TASK-10024` back down; references to them would need rewriting.

## Notes

Suggestion origin: chitty

## History

- 2026-11-26T10:54:41Z calm-ochre-quail → backlog
- 2026-11-26T10:54:44Z calm-ochre-quail: changed notes
