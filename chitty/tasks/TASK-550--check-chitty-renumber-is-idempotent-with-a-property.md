---
title: Check `chitty renumber` is idempotent with a property
status: todo
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

A cold reader's probe of this property (2026-11-22) passed in 2.5 s. Evidence that it tests something: in a scratch copy of `src/chitty`, remove `and stored.task.frontmatter.provisional` from `_plan_provisional_renumbering` (`src/chitty/store.py`) and the `is not provisional` raise in `plan_renumbering` (`src/chitty/renumbering.py`); run the property against it with `PYTHONPATH` set to the copy, confirm it fails on the second run's `nothing to renumber` assertion, and record that in a note.

## Acceptance Criteria

- [ ] `test_renumber_is_idempotent` passes; a note records it failing against the two-part mutant in the Description; `make check` passes

## History

- 2026-11-22T03:23:05Z lively-zinc-newt → planning
- 2026-11-22T04:29:43Z lively-zinc-newt: changed description
- 2026-11-22T04:29:43Z lively-zinc-newt planning → cold-read
- 2026-11-22T04:31:55Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T04:31:55Z lively-zinc-newt cold-read → todo
