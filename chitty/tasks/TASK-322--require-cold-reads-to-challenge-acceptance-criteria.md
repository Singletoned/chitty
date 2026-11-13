---
title: Require cold reads to challenge acceptance criteria
status: doing
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

- [ ] The cold-read guide asks the fresh implementing reader to implement the simplest solution the written description and criteria permit, examine each criterion for vague or bundled behaviour, and report ambiguities and decisions left to the worker without silently supplying missing requirements.
- [ ] The planning guide requires the original planner to inspect the implementing read and report against each criterion and the whole ticket, asking whether a plausible minimal implementation could satisfy the criteria yet reasonably fail a good review. Challenges use concrete counterexamples, relevant varying inputs or state, distinguishing verification, and proposed criterion wording rather than speculative features.
- [ ] Before todo, each sufficiency gap is resolved by strengthening or splitting the ticket, or explicitly rejecting it as out of scope. Requirements needed to reject the implementation are written into the ticket. Serious revisions require another cold read; a fresh stronger sufficiency reader is optional for uncertainty or repeated work–review failures, not mandatory.
- [ ] Fixed-text regression tests in `tests/test_guide_cold_read_sufficiency.py` verify the rendered planning and cold-read instructions, including their separate responsibilities and readiness gate, and fail before the guidance change. Update `docs/plan/pipeline-and-feedback.md` consistently; property tests are not applicable to fixed instructions with no variable input.

## Plan

Write the agreed guidance myself. Keep literal implementation and ambiguity reporting with the fresh reader; put the adversarial sufficiency judgement in the original planning session, using the actual implementation and report. Add focused rendered-guide tests first and confirm failure, update the two role guides and pipeline notes, then run format and all checks. Keep runner behaviour unchanged and leave the committed ticket ready for independent review.

## History

- 2026-11-13T19:51:42Z zesty-umber-puffin → backlog
- 2026-11-13T22:39:36Z brisk-yellow-urchin: changed description, acceptance criteria; wrote the plan
- 2026-11-13T22:39:36Z brisk-yellow-urchin backlog → doing
