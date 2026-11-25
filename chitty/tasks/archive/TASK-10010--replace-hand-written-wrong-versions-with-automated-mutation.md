---
title: Replace hand-written wrong versions with automated mutation testing in review
status: backlog
created: 2026-11-25
moved_from: TASK-JN42DN
---

## Description

Evidence (echonomicon TASK-213 and TASK-133, 2026-11-24): `chitty guide plan` asks planners to list "plausible wrong versions" in prose, run generators against each while planning, and have workers apply each edit and record the failure. In TASK-213 this produced 4 bounces. The prose edits could not be applied mechanically, one expected failure was wrong (`FileNotFoundError` vs an assertion), and later the count was wrong. In TASK-133, wrong versions were spread over three tickets. Planners end up simulating mutation testing by hand, in ticket text.

Suggestion: make mutation checking a tool, not ticket prose. Add an optional configured `mutation` check (for example `mutmut` or `cosmic-ray` limited to the files a branch changes) that the reviewer or runner executes. Survivors are reported as weak tests. Tickets then state behaviour and properties only, and the "wrong versions" bullets in `guide plan` can go. This follows the owner's rule to move work from agents to deterministic tools, and it shortens tickets a lot.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-25: merged into TASK-594.

## History

- 2026-11-25T22:28:18Z calm-ochre-quail → backlog
- 2026-11-25T22:28:20Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:29Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:31Z calm-ochre-quail backlog → archived
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-JN42DN
