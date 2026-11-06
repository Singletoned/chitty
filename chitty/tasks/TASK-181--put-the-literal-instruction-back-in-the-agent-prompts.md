---
title: Put the literal `*` instruction back in the agent prompts
status: review
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`chittyPrompt` in `src/chitty/integrations/pi/chitty.ts`, which `TASK-142` deleted in commit `2fc5a23`, told agents: "When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`." Agents now get their prompt from `chitty guide <mode> <ID>`, and that line is in no file under `src/chitty/roles/` nor in `src/chitty/guide.md`, so it has been lost.

Add the sentence to `src/chitty/roles/work.md`, `review.md` and `plan.md`, and to `src/chitty/guide.md`, because all of those agents write ticket text. `plan.md` and `guide.md` already have a bullet about backticks, so extend that; `work.md` and `review.md` get a new one. After bumping `__version__`, run `uv run chitty init` and commit `AGENTS.md` and `chitty.toml`, because a global `chitty` may be another checkout's code, because `guide.md` reaches `AGENTS.md`'s managed block only that way. `TASK-173` and `TASK-179` edit the same files, so touch only this bullet.

## Acceptance Criteria

- [x] A test in `TestGuide` in `tests/test_cli.py` shows `literal single` in `guide()` and in `guide(role)` for each of work, review and plan
- [x] `__version__` is bumped above `main`'s, and `AGENTS.md`'s managed block contains `literal single`

## Plan

Add the literal single-asterisk Markdown instruction to the existing backtick guidance in plan and guide, and add it as a focused bullet in work and review. Add a TestGuide regression covering guide() and guide(role) for all three roles, bump the package version, regenerate managed init files, run the required checks, and commit with Task: TASK-181.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: the ticket said `TASK-142` was still to delete `chittyPrompt`, but it merged while this was being read; refreshing `AGENTS.md`; and a garbled criterion. Left out: the old prompt's "never a subagent of the implementation agent", which is also gone, because the human asked only for the `*` line. `review.md` still says never to review work you did.

Same fault as the cold read of `TASK-187` found, 2026-11-05: `chitty init` needs `uv run` in a worktree, and comparing with `chitty guide` misleads inside Pi.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`, `tests/test_pi_extension.py`.

## Summary

Restored the literal single-asterisk Markdown instruction in the global guide and work, review, and plan role prompts; added TestGuide coverage; bumped Chitty to 0.1.33 and regenerated AGENTS.md/chitty.toml. Verified with make check: ruff, pyright, 278 unittest cases, and Node tests pass.

## History

- 2026-11-05T09:51:14Z mellow-newt → backlog
- 2026-11-05T09:53:14Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T09:53:15Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T09:53:16Z mellow-newt backlog → todo
- 2026-11-05T14:23:24Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:23:25Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T23:30:15Z kind-jay todo → doing
- 2026-11-05T23:30:30Z kind-jay: wrote the plan
- 2026-11-05T23:40:00Z kind-jay: ticked acceptance criteria
- 2026-11-05T23:40:28Z kind-jay: changed summary
- 2026-11-05T23:40:28Z kind-jay doing → review
- 2026-11-05T23:40:36Z kind-jay: ticked acceptance criteria
- 2026-11-06T14:41:27Z able-yellowhammer: changed notes
- 2026-11-06T14:41:27Z able-yellowhammer review → doing
- 2026-11-06T16:15:40Z mellow-toad: changed acceptance criteria
- 2026-11-06T16:15:41Z mellow-toad: ticked acceptance criteria
- 2026-11-06T16:15:42Z mellow-toad: changed acceptance criteria
- 2026-11-06T16:15:43Z mellow-toad: ticked acceptance criteria
- 2026-11-06T16:15:52Z mellow-toad: changed summary
- 2026-11-06T16:15:52Z mellow-toad doing → review
