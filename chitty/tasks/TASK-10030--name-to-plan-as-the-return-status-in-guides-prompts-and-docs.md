---
title: Name `to-plan` as the return status in guides, prompts and docs
status: doing
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-10029
parent: TASK-10026
created: 2026-11-25
moved_from: TASK-MHMNG8
---

## Description

Part of `TASK-10026`, after `TASK-10029` makes `to-plan` the return status and refuses returns to `planning`. Until this lands, an agent following the old text gets that refusal, which names `to-plan`.

Replace `planning` with `to-plan` where it names the status a ticket is returned to, or the status that lists waiting tickets, with no other wording change, in: the `work` and `review` continuation prompts in `src/chitty/run.py`; `src/chitty/roles/work.md`; `src/chitty/roles/review.md`; `src/chitty/guide-runner.md` and its fixture `tests/fixtures/guide-runner-expected.md`; `scripts/worker_trial/lean-work.md`; `README.md` (the return and `list -s planning` examples, and the default-status list); `docs/plan/cli.md` (default statuses); and `docs/plan/task-file.md` (add `to-plan` to the status list, and say `planning` means a planner has the ticket). Do not edit the managed block in `AGENTS.md`; `chitty init` refreshes it after landing.

Word for word replacements only, so the guides do not grow. Out of scope: `src/chitty/roles/plan.md` (`TASK-10033`).

## History

- 2026-11-25T23:09:28Z golden-coral-stoat → backlog
- 2026-11-25T23:12:24Z golden-coral-stoat backlog → todo
- 2026-11-25T23:12:53Z golden-coral-stoat: renumbered from TASK-MHMNG8
- 2026-11-26T10:55:25Z tidy-silver-puffin todo → doing
