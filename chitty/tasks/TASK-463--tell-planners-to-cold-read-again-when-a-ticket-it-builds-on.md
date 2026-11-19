---
title: Tell planners to cold-read again when a ticket it builds on lands
status: review
labels:
  - untestable
owner: untestable
created: 2026-11-19
---

## Description

A ticket planned against another ticket's unfinished output (a function, format, file or document that the other ticket adds or changes) is cold-read against a description of code that does not exist yet. When the dependency lands differently, nothing makes the planner look again: the worker builds against the landed code and the gap surfaces in review. Evidence: in injustice-league (2026-11-13), `TASK-1` was cold-read while `ARCHITECTURE.md` was absent, then implemented after that contract changed without a fresh read; missing malformed URL-port cases surfaced only through three failed reviews. In this repository on 2026-11-19, `TASK-450` was written against `_run_logged` from `TASK-353` and `TASK-426`, neither landed, and its cold reader stopped on exactly that.

Change `src/chitty/roles/plan.md`, keeping the advice general because the guide reaches every repository that uses Chitty. Add a bullet near the one about re-checking claims about other tickets before promoting:

- A ticket that builds on what an unfinished ticket adds or changes, not only on it landing first, stays in `planning` with a note naming that ticket. When that ticket is done, check this one against what landed, cold-read it again, then move it to `todo`. A ticket that only has to land after another, with nothing of the other ticket's in its description, can go to `todo` with `depends_on`.

`src/chitty/roles/plan.md` has guide tests; if one pins the bullet list, update it in a new `tests/test_guide_plan_dependency_reread.py` that checks the new bullet's key phrases (`stays in \`planning\``, `cold-read it again`), following `tests/test_guide_plan.py`.

## Notes

Suggestion origin: injustice-league

## Summary

Added the bullet after "Re-check claims about other tickets" in `src/chitty/roles/plan.md`: a ticket built on what an unfinished ticket adds or changes stays in `planning` with a note naming it, and is checked against what landed and cold-read again before `todo`; a ticket that only lands after another can go to `todo` with `depends_on`. No existing test pinned the bullet list; added `tests/test_guide_plan_dependency_reread.py` anyway (4 phrases, all 4 fail without the bullet). `make check` passes (778 tests).

## History

- 2026-11-19T20:55:40Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:41Z sunny-white-dormouse: changed notes
- 2026-11-19T21:21:14Z sunny-white-dormouse: changed title, labels, owner, description
- 2026-11-19T21:21:14Z sunny-white-dormouse backlog → todo
- 2026-11-19T21:42:20Z daring-amber-kestrel todo → doing
- 2026-11-19T21:43:31Z daring-amber-kestrel: changed summary
- 2026-11-19T21:43:31Z daring-amber-kestrel doing → review
