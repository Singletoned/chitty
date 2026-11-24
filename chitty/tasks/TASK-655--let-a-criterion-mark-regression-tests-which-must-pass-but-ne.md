---
title: Let a criterion mark regression tests, which must pass but need not fail without the change
status: doing
labels:
  - untestable
priority: high
owner: untestable
created: 2026-11-24
---

## Description

The review rules give no way to pass a test that pins behaviour the change must keep. `src/chitty/roles/review.md` (the bullet starting "For each test a criterion needs") and the last sentence of the review-note paragraph in `src/chitty/guide-runner.md` (which reaches every repository's `AGENTS.md` managed block) say a test criterion passes only with evidence that the test fails without the change. A test that pins existing behaviour, such as a refactor's check that an error message is unchanged, passes on the merge base by design, so it can never pass review. Seen on 2026-11-23 and 2026-11-24: `TASK-598`'s finished work failed review three times on this alone. `TASK-653` and `TASK-654` have tests of the same kind.

Decided with the person, 2026-11-24: a criterion may mark tests as regression tests, by listing them after the words `Regression tests:`, for example "Regression tests: `test_a`, `test_b`." A regression test must pass after the change; it is not expected to fail without it. Every other test a criterion names must still fail without the change. This replaces this ticket's earlier proposal (accepting a named wrong version as the evidence).

"Regression test" is used today, in `src/chitty/roles/work.md`, for a bug fix's test that must fail without the fix. That use changes to "a test for a bug fix", so the term has one meaning.

Change:

- `src/chitty/roles/review.md`: in that bullet, replace "For each test a criterion needs" with "For each test a criterion needs, other than a regression test it marks", and replace "If the test passes without the change, the criterion fails with cause `tests`." with "If it passes without the change, the criterion fails with cause `tests`, unless the criterion marks it as a regression test, which only has to pass."
- `src/chitty/guide-runner.md`: replace "A test criterion passes only with evidence that the test fails without the change." with "A test criterion passes only with evidence that the test fails without the change, except a test the criterion marks as a regression test, which only has to pass."
- `src/chitty/roles/plan.md`: as the first sub-bullet of the bullet starting "When the code a ticket tests already exists", add "List a test of behaviour the change must keep after `Regression tests:` in its criterion: it must pass, and need not fail without the change." Leave the wrong-version sub-bullets, which check that the other tests are strong enough.
- `src/chitty/roles/work.md`: replace "For a requested regression test" with "For a requested test of a bug fix".
- `docs/plan/pipeline-and-feedback.md`: replace the bullet "A test criterion passes only with evidence that the test fails without the change." (in the review-note list, about line 199) with the same text as the new `guide-runner.md` sentence; and after the sentence ending "Committed hand-written wrong versions add clutter and drift.", add "A criterion may mark tests that pin kept behaviour as regression tests, which must pass but need not fail without the change (2026-11-24, after `TASK-598` failed review three times because such tests pass on the merge base)."

After this lands, `chitty init` in the main checkout refreshes the managed block (`TASK-212`); do not edit `AGENTS.md` on a ticket branch.

## Acceptance Criteria

- [ ] In `src/chitty/roles/review.md`, the bullet starting "For each test a criterion needs" exempts tests the criterion marks as regression tests from both the fail-without-the-change check and the `tests` failure, and says they only have to pass
- [ ] In `src/chitty/guide-runner.md` and the review-note list in `docs/plan/pipeline-and-feedback.md`, the sentence "A test criterion passes only with evidence that the test fails without the change" carries the same regression-test exception
- [ ] `src/chitty/roles/plan.md` has the new sub-bullet first under "When the code a ticket tests already exists", naming the `Regression tests:` form; `src/chitty/roles/work.md` says "For a requested test of a bug fix"; `pipeline-and-feedback.md` has the dated decision sentence
- [ ] `make check` passes

## Summary

Done on branch `task-655` (commit `ebc571ab`): every change listed in the description, wrapped to 80 columns; `tests/fixtures/guide-runner-expected.md` regenerated from `managed_guide("runner")`. `make check` passes. After landing, `chitty init` in the main checkout refreshes the `AGENTS.md` managed block.

## History

- 2026-11-24T09:27:29Z sunny-hazel-gannet → todo
- 2026-11-24T22:31:46Z sunny-hazel-gannet: changed title, description
- 2026-11-24T22:31:46Z sunny-hazel-gannet todo → planning
- 2026-11-24T22:33:04Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T22:33:18Z sunny-hazel-gannet: changed description
- 2026-11-24T22:34:08Z sunny-hazel-gannet planning → todo
- 2026-11-24T22:56:01Z mellow-teal-jay: changed summary
- 2026-11-24T23:16:38Z human todo → doing
