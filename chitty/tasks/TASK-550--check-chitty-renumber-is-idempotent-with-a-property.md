---
title: Check `chitty renumber` is idempotent with a property
status: blocked
depends_on:
  - TASK-392
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-392` on 2026-11-22. `chitty renumber` with no `PATH` (`TASK-392`, landed; tests in `TestCliProvisionalRenumbering` in `tests/test_renumber_provisional.py`) is meant to be idempotent. This ticket adds a generated property for that.

- Add a module-level helper `build_provisional_repo(root: Path, provisional: int) -> None` in `tests/test_renumber_provisional.py`: write `chitty.toml` from `tests.support.CONFIG` with `autocommit = false` replaced by `autocommit = true`; `git init -b main`, local `user.name` and `user.email`; commit one numeric ticket with `chitty add "Numbered" -d "Fixture."` on `main`; `git switch -c feature`; add `provisional` tickets with `chitty add "P<i>" -d "Fixture."`; `git switch main`; `git merge feature`. Run the `chitty` commands with the test's `run_cli` while the working directory is `root`. `TestCliProvisionalRenumbering.fixture()` may call it, but need not.
- Property `test_renumber_is_idempotent` in `TestCliProvisionalRenumbering`, Hypothesis with `@settings(max_examples=5, deadline=None)`, drawing `provisional` from 0 to 3. Each example builds a fresh repository in `tempfile.mkdtemp(dir=self.tmp)`, `os.chdir`s into it and back in a `finally`. The first `chitty renumber` prints exactly `provisional` `renumbered` lines on stdout; the second prints `nothing to renumber` on stderr and leaves `git rev-parse HEAD` and every file's bytes under `chitty/` unchanged.
- Out of scope: archived tickets and tickets that mention each other (covered by `TestPrepareRenumbering`).

A cold reader's probe of this property (2026-11-22) passed in 2.5 s. Evidence that it tests something: in a scratch copy of `src/chitty`, remove `and stored.task.frontmatter.provisional` from `_plan_provisional_renumbering` (`src/chitty/store.py`) and the `is not provisional` raise in `plan_renumbering` (`src/chitty/renumbering.py`); run the property against it with `PYTHONPATH` set to the copy, confirm the property fails (on either run's assertion; with the numeric ticket present it fails on the first run's line count), and record that run in a note.

## Acceptance Criteria

- [ ] `test_renumber_is_idempotent` passes; a note records it failing (on any of its assertions) against the two-part mutant in the Description; `make check` passes

## Plan

Add generated repository fixture and idempotence property, verify the specified mutant fails, then run checks and commit.

## Notes

The specified two-part mutant fails the first-run line-count assertion, not the required second-run `nothing to renumber` assertion: `PYTHONPATH=tmp/mutant .venv/bin/python -m unittest tests.test_renumber_provisional.TestCliProvisionalRenumbering.test_renumber_is_idempotent` falsifies with provisional=0, 1 != 0. The required numeric ticket is already selected by the mutant on the first run. Please decide how to change the mutant or fixture/assertions while retaining meaningful evidence. The unmodified property passes. The second-run mutant assertion cannot be verified as written because the first assertion stops it; full checks and final formatting remain unfinished.

The specified two-part mutant fails the first-run line-count assertion, not the required second-run `nothing to renumber` assertion: `PYTHONPATH=tmp/mutant .venv/bin/python -m unittest tests.test_renumber_provisional.TestCliProvisionalRenumbering.test_renumber_is_idempotent` falsifies with provisional=0, 1 != 0. The required numeric ticket is already selected by the mutant on the first run. Please decide how to change the mutant or fixture/assertions while retaining meaningful evidence. The unmodified property passes. The second-run mutant assertion cannot be verified as written because the first assertion stops it. Partial implementation is committed; `make check` timed out after 120 seconds and remains unverified.

Replanned 2026-11-22: failing on the first run's count under the mutant is accepted evidence.

Check failed before this session: check exited with status 2; output in `.chitty/check.log`

The configured check failed because the unrelated staged file `tmpt1qelkfu/example.py` is not Ruff-formatted (`.chitty/check.log`). Its origin is unknown, so I left it untouched. The owner of that staged file needs to resolve or remove it from this worktree before `make check` and the clean-worktree review transition can be verified. The specified mutant failure is already recorded above; the existing property and fixture are committed.

Blocked: the owner of the unrelated staged `tmpt1qelkfu/example.py` must resolve or remove it. Its Ruff formatting failure prevents `make check`, and its staged presence prevents the clean-worktree review transition. I left the unrecognized file untouched. See `.chitty/check.log` for the failure; verification remains unfinished.

## History

- 2026-11-22T03:23:05Z lively-zinc-newt → planning
- 2026-11-22T04:29:43Z lively-zinc-newt: changed description
- 2026-11-22T04:29:43Z lively-zinc-newt planning → cold-read
- 2026-11-22T04:31:55Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T04:31:55Z lively-zinc-newt cold-read → todo
- 2026-11-22T05:05:38Z kind-ochre-newt todo → doing
- 2026-11-22T05:08:04Z kind-ochre-newt: wrote the plan
- 2026-11-22T05:08:44Z kind-ochre-newt: changed notes
- 2026-11-22T05:10:55Z kind-ochre-newt: changed owner, notes
- 2026-11-22T05:10:55Z kind-ochre-newt doing → planning
- 2026-11-22T05:12:04Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-22T05:12:04Z lively-zinc-newt planning → todo
- 2026-11-22T05:13:38Z upbeat-khaki-otter todo → doing
- 2026-11-22T05:13:41Z upbeat-khaki-otter: changed notes
- 2026-11-22T05:13:58Z upbeat-khaki-otter: changed notes
- 2026-11-22T05:14:03Z upbeat-khaki-otter: changed notes
- 2026-11-22T05:14:03Z upbeat-khaki-otter doing → blocked
