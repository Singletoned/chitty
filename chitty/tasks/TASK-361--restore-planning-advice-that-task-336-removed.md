---
title: Restore planning advice that TASK-336 removed
status: todo
owner: open-russet-eel
created: 2026-11-16
---

## Description

`TASK-336` (commit `989a26a`) made cold reads read-only, but its rewrite of `src/chitty/roles/plan.md`, `src/chitty/roles/cold-read.md` and `docs/plan/pipeline-and-feedback.md` also removed advice outside its scope and introduced wrong wording. Restore and correct it, keeping the read-only procedure.

Restore in `src/chitty/roles/plan.md` (text as before `989a26a`; `git show 989a26a^:src/chitty/roles/plan.md`):
- `Err on the side of splitting` and `About five criteria is the limit; split larger work.`
- `Use its optional` `parent` `field to group flat IDs.`
- `Ask whether odd existing behaviour is a bug before writing around it.`
- `Write requirements needed to reject the implementation into the ticket` (989a26a changed `implementation` to `finding`, which reverses the meaning) and `Give the outcomes in your reply, not in a ticket note.`
- The human ticket `that depends on this one`, `because they can land during the read`, `it is not your planning step`, and `to process completed tickets in one batch`.

Remove from `src/chitty/roles/plan.md`: the sentence starting `Keep the reader's starting point`, the added `Split a ticket when the requirements cannot be verified together.`, and the ticket ID in `(TASK-323)`. Guides reach every repository, so no guide may name a ticket ID.

In `src/chitty/roles/cold-read.md`: remove the closing paragraph (the `Use these report headings exactly` list and the `expected route` sentences, which address the planner, not the reader) and the bullet sentence `Every ticket gets one read-only cold read`; indent bullet continuation lines like the other guides. Also restore the bullet asking the reader to examine every criterion for vague phrases, bundled behaviours and a criterion that would pass with nothing built, which `989a26a` dropped, and the closing clause `the planner who started you records each finding's outcome`.

In `docs/plan/pipeline-and-feedback.md`, restore the bullet `In this repository readers run on Haiku ... so chitty run leaves it alone.`

Out of scope: any other change to the read-only procedure. No property tests: fixed text with no input; the restored phrases are a small fixed set, each listed here and tested.

## Acceptance Criteria

- [ ] Flattened `guide("plan")` contains each restored phrase listed in the description and none of `Keep the reader's starting point`, `cannot be verified together`, `reject the finding into the ticket`. A test in `tests/test_guide_plan_restored.py` checks each phrase as a subtest and fails before the change. `test_plan_uses_current_paths_as_starting_point` in `tests/test_guide_cold_read_notes.py`, which asserts the removed sentence, is deleted.
- [ ] No rendered role guide (`guide(role)` for every name in `ROLE_NAMES`) and no `src/chitty/guide*.md` file matches `TASK-[0-9]`; flattened `guide("cold-read")` contains none of `Use these report headings exactly`, `expected route`, `Every ticket gets one read-only cold read`, and still passes `tests/test_guide_read_only_cold_read.py`. Tested in the same file; fails before the change.
- [ ] `docs/plan/pipeline-and-feedback.md` contains `readers run on Haiku` and `the ticket keeps an owner`. `make check` passes.

## History

- 2026-11-16T13:04:45Z open-russet-eel → planning
- 2026-11-16T13:04:56Z open-russet-eel: changed owner
- 2026-11-16T13:04:56Z open-russet-eel planning → cold-read
- 2026-11-16T13:10:43Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T13:10:43Z open-russet-eel cold-read → planning
- 2026-11-16T13:10:45Z open-russet-eel planning → todo
