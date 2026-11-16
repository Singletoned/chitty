---
title: Return a ticket to planning for any defect in the ticket
status: cold-read
owner: open-russet-eel
created: 2026-11-16
---

## Description

Workers and reviewers can already return a ticket to `planning` (`TASK-323`), but the guides allow it only for missing or contradictory requirements or an unresolved design decision. With read-only cold reads (`TASK-336`), workers and reviewers become the main check on tickets, so widen the trigger to any defect in the ticket.

A ticket defect is any of these six, written with these exact phrases:

- `missing or contradictory requirements`
- `an unresolved design decision`
- `a wrong claim about the code, files or other tickets`
- `a criterion that cannot be verified as written or would pass with nothing built`
- `a criterion that contradicts the description`
- `a ticket too large to finish in one session`

Unchanged: the worker still chooses cheap-to-reverse defaults and notes them; the reviewer still sends implementation defects against clear requirements to `doing`, and uses `Review failed (design):` for a planning return; `blocked` stays for external obstacles; the note still gives the discovery, why the ticket cannot guide the work, and the decision needed. The store validation from `TASK-323` does not change.

Files: `src/chitty/roles/work.md` and `src/chitty/roles/review.md` (the bullet starting `For missing or contradictory requirements`), `continuation_prompt` in `src/chitty/run.py`, `src/chitty/guide-runner.md`, the return-to-planning paragraph of `README.md`, and the first bullets of `docs/plan/pipeline-and-feedback.md`. Do not edit `AGENTS.md` or run `chitty init`: the main checkout updates the managed block after landing. Leave `tests/fixtures/guide-before-workflow.md` alone; it is a fixture of old text.

Out of scope: telling them to list every problem in one note (`TASK-354`), and any code change to status validation.

No property tests: fixed text, and the defects are a small fixed set, each listed here and each tested.

## Acceptance Criteria

- [ ] The rendered `chitty guide work` and `chitty guide review` each contain all six defect phrases as reasons to set `-s planning`, and still contain `For a cheap-to-reverse default, choose it` (work) and `implementation defects against clear requirements` (review). A test in `tests/test_guide_return_scope.py` checks each phrase in each role as a separate subtest and fails before the change; `tests/test_guide_return_to_planning.py` is updated to the new wording.
- [ ] `continuation_prompt` for both `work` and `review` offers `planning` for `a defect in the ticket` and still offers `blocked`; `src/chitty/guide-runner.md` names the six defects. Tested in the same file; the test fails before the change.
- [ ] The return-to-planning paragraph in `README.md` and the bullets in `docs/plan/pipeline-and-feedback.md` describe the same six defects. `make check` passes.

## History

- 2026-11-16T12:50:58Z open-russet-eel → planning
- 2026-11-16T12:51:14Z open-russet-eel: changed owner
- 2026-11-16T12:51:14Z open-russet-eel planning → cold-read
