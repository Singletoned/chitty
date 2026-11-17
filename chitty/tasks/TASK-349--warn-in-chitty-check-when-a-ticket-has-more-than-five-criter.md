---
title: Warn in chitty check when a ticket has more than five criteria
status: cold-read
created: 2026-11-16
---

## Description

`src/chitty/roles/plan.md` says about five criteria is the limit and to split larger tickets. Make `chitty check` warn about a ticket in `planning` or `todo` that has more than five criteria, then point the guide at the warning.

Add the warning in `check()` in `src/chitty/check.py`, as a `Problem` with severity `warning`, like `_markdown_warnings`. Put the limit in a module-level constant `MAX_CRITERIA = 5`. The message names the count and the limit, for example `6 acceptance criteria; split tickets above 5`. A warning does not change the exit code of `chitty check`, and `chitty edit` keeps ignoring warnings.

Tests use Hypothesis, as `tests/test_property_next.py` does, and go in a new file `tests/test_check_criteria_limit.py`.

Out of scope: warning from `chitty edit` or `chitty add`, configuring the limit, and counting checks inside one criterion.

## Acceptance Criteria

- [ ] Property test with Hypothesis: for any status in `STATUSES` from `src/chitty/model.py`, any number of criteria from 0 to 10, and the ticket archived or not, `check()` returns exactly one warning-severity criteria-limit problem for that ticket when the status is `planning` or `todo` and the count is above `MAX_CRITERIA`, and none otherwise. The test fails on `main` today, which has no such warning.
- [ ] `chitty check` on a repository whose only problem is a `todo` ticket with six criteria prints a line containing `warning:` and the ticket path, and exits 0.
- [ ] In `src/chitty/roles/plan.md`, the sentence `About five criteria is the limit; split larger work.` becomes `chitty check` warns above five criteria; split larger work. (with `chitty check` in backticks), and the matching phrase in `tests/test_guide_plan_restored.py` is updated. `make check` passes.

## History

- 2026-11-16T10:00:01Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:44Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:00:58Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:00:58Z kind-umber-toad planning → cold-read
