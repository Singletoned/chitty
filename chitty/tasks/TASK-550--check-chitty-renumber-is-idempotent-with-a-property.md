---
title: Check `chitty renumber` is idempotent with a property
status: cold-read
depends_on:
  - TASK-392
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-392` on 2026-11-22. After `TASK-392`, `chitty renumber` with no `PATH` is meant to be idempotent: a person or script can run it at any time. This ticket adds a generated property for that. `TASK-392` landed `TestCliProvisionalRenumbering` (with `fixture()`) in `tests/test_renumber_provisional.py` (rechecked 2026-11-22); reuse its setup steps.

Hypothesis property in `tests/test_renumber_provisional.py` (`max_examples` small, `deadline=None`): for 0 to 3 provisional tickets, each active or archived, optionally one mentioning another, the first `chitty renumber` prints exactly that many `renumbered` lines to stdout, and the second prints `nothing to renumber` to stderr and leaves every file byte-identical. Build a fresh repository inside each example (its own `tempfile.mkdtemp(dir=self.tmp)`), `os.chdir` into it and back afterwards, since `CliTestCase.setUp` changes into `self.root` once per test. Fixture per example as `TASK-392`'s: `autocommit = true`, `git init -b main`, local author, provisional tickets made with `chitty add` on `feature` and merged into `main`.

## Acceptance Criteria

- [ ] The property passes, and fails against a `renumber_provisional` patched to renumber even IDs that are already numeric (or another named mutant, recorded in a note); `make check` passes

## History

- 2026-11-22T03:23:05Z lively-zinc-newt → planning
- 2026-11-22T04:29:43Z lively-zinc-newt: changed description
- 2026-11-22T04:29:43Z lively-zinc-newt planning → cold-read
