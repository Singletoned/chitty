---
title: Let review accept a named wrong version as evidence for a test that guards unchanged behaviour
status: todo
labels:
  - untestable
priority: high
owner: untestable
created: 2026-11-24
---

## Description

The review rules contradict the planning guide. `src/chitty/roles/plan.md` (the bullet starting "When the code a ticket tests already exists") tells planners that a stub cannot show such tests fail without the change, and to list plausible wrong versions instead. But `src/chitty/roles/review.md` (the bullet starting "For each test a criterion needs") and the last sentence of the review-note paragraph in `src/chitty/guide-runner.md` (which reaches every repository's `AGENTS.md` managed block) say a test criterion passes only with evidence that the test fails without the change. Reviewers follow their own guide, so a ticket whose guard tests are specified with wrong versions can never pass review. Seen on 2026-11-23 and 2026-11-24: `TASK-598`'s finished work failed review three times on this conflict alone, the last time after the reviewer had run every wrong version and seen each fail its named test. `TASK-653` and `TASK-654` are planned the same way.

Change, with no net growth in either guide:

- `src/chitty/roles/review.md`: in that bullet, replace "If the test passes without the change, the criterion fails with cause `tests`." with "If it passes without the change, the criterion fails with cause `tests`, unless the ticket says the test guards behaviour the change keeps and names a wrong version for it: then show that it fails against that wrong version."
- `src/chitty/guide-runner.md`: replace "A test criterion passes only with evidence that the test fails without the change." with "A test criterion passes only with evidence that the test fails without the change, or, for a guard test, against the wrong version the ticket names."

`plan.md` needs no change. After this lands, `chitty init` in the main checkout refreshes the managed block (`TASK-212`); do not edit `AGENTS.md` on a ticket branch.

## History

- 2026-11-24T09:27:29Z sunny-hazel-gannet → todo
