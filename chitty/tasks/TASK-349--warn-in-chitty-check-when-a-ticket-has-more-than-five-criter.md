---
title: Warn in chitty check when a ticket has more than five criteria
status: review
created: 2026-11-16
---

## Description

`src/chitty/roles/plan.md` says about five criteria is the limit and to split larger tickets. Make `chitty check` warn about a ticket in `planning` or `todo` that has more than five criteria, then point the guide at the warning.

Add the warning in `check()` in `src/chitty/check.py`, as a `Problem` with severity `warning`, like `_markdown_warnings`. Put the limit in a module-level constant `MAX_CRITERIA = 5`. The message is exactly `<N> acceptance criteria; split tickets above 5`, where N is the count. Only status and count matter: an archived ticket in `planning` or `todo` warns too. A warning does not change the exit code of `chitty check`, and `chitty edit` keeps ignoring warnings.

Tests use Hypothesis, as `tests/test_property_next.py` does, and go in a new file `tests/test_check_criteria_limit.py`, inheriting `RepoTestCase` from `tests/support.py` and using its config, so no setup warning appears.

Out of scope: warning from `chitty edit` or `chitty add`, configuring the limit, and counting checks inside one criterion.

## Acceptance Criteria

- [x] Property test with Hypothesis: generate a set of 1 to 12 tickets, each with a status from `STATUSES` in `src/chitty/model.py`, 0 to 10 criteria whose text is ASCII letters only, and archived or not. Write each example into a fresh repository (or clear `chitty/` between examples). The set of paths with a criteria-limit warning from `check()` equals the set of tickets in `planning` or `todo` with more than `MAX_CRITERIA` criteria, each warned once with the exact message. The test fails on `main` because of the missing warning, not only because `MAX_CRITERIA` cannot be imported.
- [x] `chitty check` on a repository whose only problem is a `todo` ticket with six criteria prints a line containing `warning:` and the ticket path, and exits 0.
- [x] In `src/chitty/roles/plan.md`, `About five criteria is the limit; split larger work.` is replaced with exactly `` `chitty check` warns above five criteria; split larger work. ``, and `tests/test_guide_plan_restored.py` asserts that sentence instead of the old one. The later sentence `Split rather than exceed about five criteria.` stays. `make check` passes.

## Plan

Add a module-level criteria threshold and append warning Problems during check() for parsed tickets whose status is planning or todo and whose criterion count exceeds the threshold. Test the property across generated ticket sets in a fresh RepoTestCase repository, add CLI exit/output coverage, and update the planning guide assertion and wording.

## Summary

Implemented criteria-limit warnings in check(), updated guide wording, and added property, CLI, and guide coverage. Verified with make format and make check (all pass). Follow-up: reviewer should confirm archived-ticket property coverage.

## History

- 2026-11-16T10:00:01Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:44Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:00:58Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:00:58Z kind-umber-toad planning → cold-read
- 2026-11-17T16:02:55Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:02:55Z kind-umber-toad cold-read → planning
- 2026-11-17T16:04:10Z kind-umber-toad planning → todo
- 2026-11-17T17:45:59Z rosy-zinc-jay todo → doing
- 2026-11-17T17:46:19Z rosy-zinc-jay: wrote the plan
- 2026-11-17T17:50:08Z rosy-zinc-jay: changed summary; ticked acceptance criteria
- 2026-11-17T17:50:08Z rosy-zinc-jay doing → review
