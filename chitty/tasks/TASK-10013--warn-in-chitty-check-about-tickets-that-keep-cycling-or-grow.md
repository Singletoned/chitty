---
title: Warn in `chitty check` about tickets that keep cycling or growing
status: backlog
priority: medium
created: 2026-11-25
moved_from: TASK-PT4DEM
---

## Description

Evidence (echonomicon, 2026-11-24): `TASK-133` (about 30 lines of code) had 9 cold reads, 3 worker sessions and about 1,100 words of description over only 2 criteria, so the existing 5-criterion warning never fired. `TASK-213` went `doing -> planning` 4 times over ticket wording, never over the feature. The full case study is the archived `TASK-10015`.

`chitty guide plan` now caps cold reads at 1–2 rounds, but nothing checks it. Suggested deterministic warnings, in `chitty check` (or on `edit -s todo`), each telling the planner to escalate to the owner or a stronger planner instead of another round:

- more than 2 transitions into `cold-read` in the ticket's History;
- more than 2 returns from `doing` to `planning`;
- a description that is long for its number of criteria.

Related: TASK-499 warns on the size of the whole ticket file. Out of scope: a model asked at each transition whether the effort is proportionate (the case study's recommendation 2); try the deterministic warnings first.

## Notes

Planner, 2026-11-25: `chitty check` already warns `3 cold reads; simplify or split instead of another read` and `specification has N words; simplify or split tickets above 500 words`. Only the warning on repeated returns from `doing` to `planning` may be left; check before planning, and archive if nothing is.

## History

- 2026-11-25T22:28:44Z calm-ochre-quail → backlog
- 2026-11-25T22:28:46Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:45Z calm-ochre-quail: changed title, priority, description
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-PT4DEM
- 2026-11-25T23:06:34Z calm-ochre-quail: changed notes
- 2026-11-25T23:07:18Z calm-ochre-quail: replaced notes
