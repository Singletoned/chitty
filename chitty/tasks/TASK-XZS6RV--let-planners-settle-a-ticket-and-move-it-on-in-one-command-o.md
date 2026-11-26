---
title: Let planners settle a ticket and move it on in one command, or guide them to chain steps
status: to-plan
created: 2026-11-26
provisional: true
---

## Description

Seen 2026-11-25, planning TASK-472. The planner ran a script of three Chitty commands: `chitty edit TASK-472 -s planning --replace-in-description ... --set-ac 1 ...`, then `chitty check <file>`, then `chitty edit TASK-472 -s todo`. The first was refused as a whole, because one `--replace-in-description` OLD text did not match. That was correct. But the script did not stop, so the last command moved the ticket to `todo` without the fixes. The planner noticed only because the output showed the refusal, and had to reapply the fixes afterwards.

Chitty already makes one `edit` atomic. The gap is the planning sequence itself (fix text, check, move to `todo`), which the plan guide describes as separate steps, so agents script it as separate commands and an early failure does not stop the later ones.

Options:
- `chitty edit -s todo` (and `-s cold-read`) runs the same per-ticket checks as `chitty check` and refuses on errors, so "edit the text and move status in one command" is enough and the separate `check` step goes.
- The plan guide says to change text and status in one `chitty edit`, which it already half says ("Change status in the same edit as the text it depends on"), and to join dependent Chitty commands with `&&`.
- Possibly: `chitty edit` refuses `-s todo` while the most recent edit of that ticket by the same actor failed. This is probably too clever; the first option is simpler.

## Notes

Suggestion origin: chitty

Decided (the person, 2026-11-26): edit -s todo and -s cold-read run the per-ticket checks of chitty check and refuse on errors; the plan guide also says to chain dependent Chitty commands with &&.

## History

- 2026-11-26T10:54:53Z calm-ochre-quail → backlog
- 2026-11-26T10:54:57Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:16Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:16Z calm-ochre-quail backlog → to-plan
