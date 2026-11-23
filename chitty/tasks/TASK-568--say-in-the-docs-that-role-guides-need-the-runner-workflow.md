---
title: Say in the docs that role guides need the runner workflow
status: done
labels:
  - untestable
owner: vivid-ginger-heron
depends_on:
  - TASK-334
created: 2026-11-22
---

## Description

After `TASK-334`, `chitty guide <role>` refuses under `workflow = "tickets"`. `README.md` (the guide commands, around lines 72-85), the Chitty section of `AGENTS.md` (around lines 69-71, outside the managed block) and `docs/plan/agent-instructions.md` (around lines 12-13) list the role guides with no workflow condition. Say there that role guides need `workflow = "runner"`. Do not edit the managed block of `AGENTS.md`.

## Notes

Decided: `AGENTS.md` -> no edit, because the ticket's "Chitty section of `AGENTS.md` (around lines 69-71, outside the managed block)" is wrong. The only role-guide list in `AGENTS.md` (lines 79-83) is inside the managed block, which comes from `src/chitty/guide-runner.md`. `managed_guide` in `src/chitty/store.py` appends that file only for `workflow = "runner"`, so a tickets repository never gets the list. The ticket forbids editing the managed block, and nothing outside it lists role guides.

Changed `README.md` (the guide paragraph after the command examples) and `docs/plan/agent-instructions.md` (the role-file bullet) to say that role guides need `workflow = "runner"`. Checked in a scratch repository created by `chitty init` (tickets by default): `chitty guide work|setup|plan` each print `Error: chitty guide <role> needs workflow = "runner" in the Chitty config`, and plain `chitty guide` works. `make check` passes (1142 tests).

Reviewed: the ticket has no numbered criteria, so each line below is one requirement from the Description.
1: pass - `README.md:86-88` now says role guides need `workflow = "runner"` and that under `workflow = "tickets"` only plain `chitty guide` works. Checked in a scratch repository after `chitty init` (tickets by default): every role in `ROLE_NAMES` (`work`, `review`, `plan`, `setup`, `repair`, `cold-read`, `rebase`) printed `Error: chitty guide <role> needs workflow = "runner" in the Chitty config`, and plain `chitty guide` printed the block.
2: pass - `docs/plan/agent-instructions.md:14-15` says the same and adds that the block leaves out the role list. Confirmed: `chitty guide | grep -c 'guide work'` printed `0` in the tickets scratch repository, and `managed_guide` in `src/chitty/store.py:1700` appends `guide-runner.md` only for `runner`.
3: pass - the Decided note on `AGENTS.md` is right. The managed block covers `AGENTS.md:62-115`, the only role-guide list is at lines 81-83 inside it, and nothing outside the block lists role guides. The ticket forbids editing the block, so not editing the file keeps to the requirement. The managed block is unchanged in the diff.
4: pass - `make check` in the worktree: `1142 passed, 791 subtests passed`.

## Summary

Docs say role guides need the runner workflow: README and docs/plan/agent-instructions.md. AGENTS.md is unchanged; see the Decided note.

## History

- 2026-11-22T09:54:44Z friendly-jade-stoat → todo
- 2026-11-23T08:23:48Z vivid-ginger-heron: changed owner
- 2026-11-23T08:23:48Z vivid-ginger-heron todo → doing
- 2026-11-23T08:27:45Z vivid-ginger-heron: changed notes, summary
- 2026-11-23T08:27:45Z vivid-ginger-heron doing → review
- 2026-11-23T08:27:56Z vivid-ginger-heron: changed summary
- 2026-11-23T10:19:15Z youthful-bronze-puffin: changed notes
- 2026-11-23T10:19:15Z youthful-bronze-puffin review → done
