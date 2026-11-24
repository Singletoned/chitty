---
title: Worker sent tickets to planning when it had only skipped the tests
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

In echonomicon on 2026-11-24, with work_model openai-codex/gpt-6-luna under chitty run, TASK-217 and TASK-219 each got an implementation commit and no tests. The worker then set them to planning with notes like 'Implementation is incomplete ... please resume implementation with those tests', which is implementation work and belongs in doing, not planning. TASK-213 was also sent to planning twice over a question the ticket already answered. Ideas: (1) chitty guide work could say outright that a missing piece of one's own work never counts as a planning blocker; (2) the runner could refuse a planning return whose branch diff touches src/ but not tests/ when the criteria name tests, or treat it as doing; (3) the work guide could tell the worker to write the tests before the implementation, since the stub-first order the planning guide asks for was skipped.

## Notes

Suggestion origin: echonomicon

Duplicate: merged into TASK-686 (sound tickets returned to planning), TASK-676 (leftover uncommitted edits) and TASK-585 (stall detection); the evidence is recorded there.

## History

- 2026-11-24T22:21:40Z zesty-coral-newt → backlog
- 2026-11-24T22:21:40Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:40Z zesty-coral-newt: changed labels, notes
