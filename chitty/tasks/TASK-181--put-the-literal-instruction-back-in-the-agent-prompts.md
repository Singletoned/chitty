---
title: Put the literal `*` instruction back in the agent prompts
status: doing
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`chittyPrompt` in `src/chitty/integrations/pi/chitty.ts`, which `TASK-142` deleted in commit `2fc5a23`, told agents: "When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`." Agents now get their prompt from `chitty guide <mode> <ID>`, and that line is in no file under `src/chitty/roles/` nor in `src/chitty/guide.md`, so it has been lost.

Add the sentence to `src/chitty/roles/work.md`, `review.md` and `plan.md`, and to `src/chitty/guide.md`, because all of those agents write ticket text. `plan.md` and `guide.md` already have a bullet about backticks, so extend that; `work.md` and `review.md` get a new one. After bumping `__version__`, run `uv run chitty init` and commit `AGENTS.md` and `chitty.toml`, because a global `chitty` may be another checkout's code, because `guide.md` reaches `AGENTS.md`'s managed block only that way. `TASK-173` and `TASK-179` edit the same files, so touch only this bullet.

## Acceptance Criteria

- [x] A test in `TestGuide` in `tests/test_cli.py` shows `literal single` in `guide()` and in `guide(role)` for each of work, review and plan
- [ ] The ticket branch leaves the managed `AGENTS.md` block, `chitty.toml`, and `__version__` unchanged; the guide sources carry the instruction for setup regeneration on main after landing.

## Plan

Add the literal single-asterisk Markdown instruction to the existing backtick guidance in plan and guide, and add it as a focused bullet in work and review. Add a TestGuide regression covering guide() and guide(role) for all three roles, bump the package version, regenerate managed init files, run the required checks, and commit with Task: TASK-181.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Fixed: the ticket said `TASK-142` was still to delete `chittyPrompt`, but it merged while this was being read; refreshing `AGENTS.md`; and a garbled criterion. Left out: the old prompt's "never a subagent of the implementation agent", which is also gone, because the human asked only for the `*` line. `review.md` still says never to review work you did.

Same fault as the cold read of `TASK-187` found, 2026-11-05: `chitty init` needs `uv run` in a worktree, and comparing with `chitty guide` misleads inside Pi.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`, `tests/test_pi_extension.py`.

Review failed (integration): rebasing onto `main` conflicts in `chitty.toml`, `src/chitty/__init__.py`, `tests/test_cli.py`, `tests/test_pi_extension.py`.

Rebased onto `main` by a human-run session. My earlier "restore `main`'s `chitty.toml`" commit brought in `random_ids`, which this branch's older code couldn't read. Resolved:
- `chitty.toml` matches `main`'s.
- `__version__` is `0.1.36`, which `TASK-173` also takes, so whichever lands second bumps again.
- `tests/test_cli.py` keeps both sets of guide tests.
- `tests/test_pi_extension.py` compares against `__version__`.
`make check` passes (330 tests). Re-check the criteria.

This branch edits Chitty's managed block in `AGENTS.md`. Under `TASK-218`, branches may not: restore the block from `main` (`git checkout main -- AGENTS.md` if the rest of the file is unchanged) and change only `src/chitty/guide.md` or `src/chitty/roles/`. The main checkout regenerates `AGENTS.md` after landing.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Unblocked by a human-run session. All three failed reviews were rebase conflicts with `main`, mostly on `tests/test_cli.py`'s guide tests and `__version__`, not problems with the work. Rebased onto `main` (`0.1.40`):
- Both sides of each conflicting guide test are kept.
- The new `main` guide text sits alongside this ticket's change; the role files keep `TASK-219`'s sentence.
- `chitty.toml` and `AGENTS.md` match `main` (`TASK-212`, `TASK-218`).
- `__version__` is `0.1.41`.
`make check` passes (360 tests). Several open tickets also use `0.1.41`, so whichever lands second will need its version bumped again.

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/guide.md
  src/chitty/roles/plan.md
  src/chitty/roles/review.md
  src/chitty/roles/work.md
make: *** [check] Error 1

Owner set to `human` on 2026-11-07, before `chitty run --mode work` looped on it as it did 54 times on `TASK-179`: the branch has `__version__` 0.1.41 and `main` has 0.1.42, so the check fails, and in work mode a failed check only adds a note and leaves the ticket in `doing`, so no agent starts to fix it. `TASK-224` removes branch version bumps. Clear the owner once it lands.

Unparked after TASK-224 and TASK-227: branches no longer bump the version or regenerate managed setup; a doing ticket with a failed check now starts a worker. Recheck and finish the branch before review.

## Summary

Restored the literal single-asterisk Markdown instruction in guide.md and the work, review, and plan role prompts; added TestGuide coverage; bumped __version__ to 0.1.36; regenerated the managed AGENTS.md block. Verification: make check passes (ruff, pyright, 330 unittest tests, and Node tests). Follow-ups: none.

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
- 2026-11-06T16:39:56Z sunny-eel: changed notes
- 2026-11-06T16:39:56Z sunny-eel review → doing
- 2026-11-06T18:08:19Z youthful-toad: changed notes
- 2026-11-06T18:13:33Z youthful-toad: changed notes
- 2026-11-06T18:19:46Z intrepid-gannet: changed summary
- 2026-11-06T18:19:46Z intrepid-gannet doing → review
- 2026-11-06T18:35:31Z honest-marten: changed owner, notes
- 2026-11-06T18:35:31Z honest-marten review → blocked
- 2026-11-06T21:41:00Z youthful-toad: changed owner, notes
- 2026-11-06T21:41:00Z youthful-toad blocked → review
- 2026-11-06T21:49:23Z honest-ibis: changed notes
- 2026-11-06T21:49:23Z honest-ibis review → doing
- 2026-11-07T09:39:54Z vivid-dormouse: changed owner, notes
- 2026-11-08T13:05:13Z eager-puffin: changed owner, acceptance criteria, notes
