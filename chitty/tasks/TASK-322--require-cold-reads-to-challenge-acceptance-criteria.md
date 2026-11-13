---
title: Require cold reads to challenge acceptance criteria
status: error
labels:
  - workflow
  - planning
priority: high
created: 2026-11-13
moved_from: BACKLOG-10274890
---

## Description

Prevent avoidable work–review cycles caused by criteria that allow a plausible minimal implementation a good review would reject. Keep the fresh cheap-model implementing read literal; use its implementation and report as evidence for a sufficiency read in the original planning session. The planner challenges every criterion and their combined coverage, then writes missing requirements into the ticket instead of relying on conversation context. Scope: planning and cold-read guidance, the pipeline design notes, and fixed-text regression tests. No runner changes, new mandatory agent session, or guarantee of finding every defect.

## Acceptance Criteria

- [x] The cold-read guide asks the fresh implementing reader to implement the simplest solution the written description and criteria permit, examine each criterion for vague or bundled behaviour, and report ambiguities and decisions left to the worker without silently supplying missing requirements.
- [x] The planning guide requires the original planner to inspect the implementing read and report against each criterion and the whole ticket, asking whether a plausible minimal implementation could satisfy the criteria yet reasonably fail a good review. Challenges use concrete counterexamples, relevant varying inputs or state, distinguishing verification, and proposed criterion wording rather than speculative features.
- [x] Before todo, each sufficiency gap is resolved by strengthening or splitting the ticket, or explicitly rejecting it as out of scope. Requirements needed to reject the implementation are written into the ticket. Serious revisions require another cold read; a fresh stronger sufficiency reader is optional for uncertainty or repeated work–review failures, not mandatory.
- [x] Fixed-text regression tests in `tests/test_guide_cold_read_sufficiency.py` verify the rendered planning and cold-read instructions, including their separate responsibilities and readiness gate, and fail before the guidance change. Update `docs/plan/pipeline-and-feedback.md` consistently; property tests are not applicable to fixed instructions with no variable input.

## Plan

Write the agreed guidance myself. Keep literal implementation and ambiguity reporting with the fresh reader; put the adversarial sufficiency judgement in the original planning session, using the actual implementation and report. Add focused rendered-guide tests first and confirm failure, update the two role guides and pipeline notes, then run format and all checks. Keep runner behaviour unchanged and leave the committed ticket ready for independent review.

## Notes

Runner error (landing): `git merge --ff-only task-322` failed in /Users/singletoned/src/singletoned/chitty:
hint: Diverging branches can't be fast-forwarded, you need to either:
hint:
hint: 	git merge --no-ff
hint:
hint: or:
hint:
hint: 	git rebase
hint:
hint: Disable this message with "git config set advice.diverging false"
fatal: Not possible to fast-forward, aborting.
Resolve the landing problem in /Users/singletoned/src/singletoned/chitty-cold-read-sufficiency or the main checkout before retrying.

Worktree: `/Users/singletoned/src/singletoned/chitty-cold-read-sufficiency`

Error output:
```text
`git merge --ff-only task-322` failed in /Users/singletoned/src/singletoned/chitty:
hint: Diverging branches can't be fast-forwarded, you need to either:
hint:
hint: 	git merge --no-ff
hint:
hint: or:
hint:
hint: 	git rebase
hint:
hint: Disable this message with "git config set advice.diverging false"
fatal: Not possible to fast-forward, aborting.
Resolve the landing problem in /Users/singletoned/src/singletoned/chitty-cold-read-sufficiency or the main checkout before retrying.
```

## Summary

Implemented in `63b7db9`. Wrote both role guides and pipeline notes directly: the fresh reader builds the simplest literal solution and reports ambiguity; the original planner examines the implementation, tests and report against each criterion and combined coverage. Sufficiency gaps need counterexamples, distinguishing verification and proposed criteria, resolved in the ticket before `todo`; a separate stronger reader remains optional. No runner changes. All three new rendered-guide tests failed first (`FAILED (failures=23)`), then passed; updated the existing outcome-reporting test for the revised wording without dropping its intent. `make format` and `make check` pass (530 Python tests plus Node tests). Fixed-text guidance has no variable-input property. Guidance tests verify instruction delivery, not actual model compliance. Committed and ready for independent review; not merged.

## History

- 2026-11-13T19:51:42Z zesty-umber-puffin → backlog
- 2026-11-13T22:39:36Z brisk-yellow-urchin: changed description, acceptance criteria; wrote the plan
- 2026-11-13T22:39:36Z brisk-yellow-urchin backlog → doing
- 2026-11-13T22:42:38Z brisk-yellow-urchin: changed summary; ticked acceptance criteria
- 2026-11-13T22:42:38Z brisk-yellow-urchin doing → review
- 2026-11-13T23:25:49Z youthful-ebony-ibis: changed notes
- 2026-11-13T23:25:49Z youthful-ebony-ibis review → error
