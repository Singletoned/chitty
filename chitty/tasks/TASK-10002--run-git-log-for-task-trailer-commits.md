---
title: Run `git log` for `Task:` trailer commits
status: done
depends_on:
  - TASK-358
created: 2026-11-23
moved_from: TASK-YJ6VBS
---

## Description

Split from `TASK-358` on 2026-11-23 after its third cold read. `TASK-358` adds `TrailerCommit`, `TRAILER_LOG_OPTIONS` and the pure `parse_trailer_log` in `src/chitty/git.py`; this ticket runs `git log` and feeds them. `TASK-571` calls it from `chitty check`.

Decision, in `src/chitty/git.py`: new `trailer_commits(root: Path, ref: str) -> list[TrailerCommit]`. One `git log <ref>` call with `TRAILER_LOG_OPTIONS`, run with `subprocess.run(check=False, cwd=root, capture_output=True)` as `changed_paths` does: stdout is bytes (not `text=True`, which rewrites `\r`). A non-zero exit raises `ChittyError` naming the command and `root`, with Git's stderr, as `changed_paths` does. Stdout is decoded as UTF-8; a `UnicodeDecodeError` is raised as `ChittyError` naming the ref, so a non-UTF-8 path fails loudly. The text goes to `parse_trailer_log`; the result is newest first, as Git prints. Why the options: `--no-renames`, so a file moved from `src/` into `chitty/tasks/` lists both paths; `--root`, `--no-show-signature` and `--encoding=UTF-8`, so user config (`log.showRoot`, `log.showSignature`, `i18n.logOutputEncoding`) cannot change the bytes. Nothing calls `trailer_commits` yet.

Tests: add real-Git examples to `tests/test_trailer_commits.py` (which `TASK-358` added with only Hypothesis tests), in a class inheriting `RepoTestCase` from `tests/support.py`. It points `HOME` and `XDG_CONFIG_HOME` at temp directories and sets `init.defaultBranch=main`, so the user's global Git config (for example `commit.gpgsign=true`) is not read. Run `git init` in the temp repository and set `user.name` and `user.email` there. Build the `\xff` tree by passing bytes to `git mktree` (`input=b"..."`), not text. `--no-show-signature` has no failing test: proving it needs a signed commit, and signing is not portable to CI. No property: the parser's properties are in `TASK-358`; this is the wiring to one external process, a fixed set of cases.

- Three commits: the root, with subject `Add ü` and two `Task:` trailers, changing `src/a.py` and `src/b\rc.py`; one whose only path is `chitty/tasks/TASK-1 ü "q".md`; one with subject `chitty: edit TASK-1` and no change (`--allow-empty`). Assert the bytes `git log main` prints with `TRAILER_LOG_OPTIONS` equal the layout `TASK-358` describes, built in the test from the known SHAs, and that `trailer_commits(root, "main")` returns the three commits field by field.
- Config: set `log.showSignature=true`, `i18n.logOutputEncoding=ISO-8859-1` and `log.showRoot=false` in that repository; `trailer_commits` returns the same commits. (Without `--root`, `log.showRoot=false` drops the root commit's paths.)
- Non-UTF-8: add a commit whose tree holds a path with byte `\xff`, built with `git mktree` and `git commit-tree` (some file systems refuse such names); `trailer_commits` raises `ChittyError`.
- Unknown ref: `trailer_commits(root, "nope")` raises `ChittyError` whose message contains `git log` and the root.

## Acceptance Criteria

- [x] The three-commit example passes: the exact `git log` bytes match the layout and `trailer_commits` returns the three commits field by field
- [x] `make check` passes
- [x] The config, non-UTF-8 and unknown-ref tests pass; each fails when the matching handling is removed (drop `--root` or `--encoding=UTF-8` from `TRAILER_LOG_OPTIONS`, decode with `errors="replace"`, use `check=True`). Record those four runs in a note

## Plan

Add real Git wiring tests and verify mutations, then implement byte-preserving log execution and run checks.

## Notes

Planner, 2026-11-23: `TASK-358` landed `TrailerCommit`, `TRAILER_LOG_OPTIONS` and `parse_trailer_log` as this ticket assumes; cold-read against what landed.

Regression verification: before implementation pytest failed to import trailer_commits. With implementation, removing --root or --encoding=UTF-8 each failed test_config; replacing invalid UTF-8 failed test_invalid_utf8; changing to check=True failed test_unknown_ref. Restored code passes make check.

Reviewed: `trailer_commits` in `src/chitty/git.py` matches the ticket (one `git log <ref>` with `TRAILER_LOG_OPTIONS`, bytes stdout, `ChittyError` with command, root and stderr on failure, `ChittyError` naming the ref on bad UTF-8); reviewed by hand from the main session because the runner reads this provisional ticket from `main` and never saw it in `review`.
1: pass - `pytest tests/test_trailer_commits.py`: 7 passed; `test_log` checks the exact bytes against `render` and the three commits field by field. With the branch's test file at the merge base (temporary worktree), collection fails: `ImportError: cannot import name 'trailer_commits' from 'chitty.git'`.
2: pass - after rebasing onto `main` (`0ce50010`), `make check`: 1165 passed.
3: pass - each mutation run by hand and restored: dropping `--root` failed `test_config` (AssertionError); dropping `--encoding=UTF-8` failed `test_config` (ChittyError); `errors="replace"` failed `test_invalid_utf8`; `check=True` failed `test_unknown_ref` (CalledProcessError).

## Summary

Implemented byte-preserving Git log execution with real Git tests. make check passed; all four required mutations failed their corresponding tests.

## History

- 2026-11-23T18:39:16Z witty-yellow-vole → planning
- 2026-11-23T19:28:36Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:38:32Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T19:38:32Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:38:47Z witty-yellow-vole: replaced notes
- 2026-11-23T19:38:47Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:39:49Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:39:52Z witty-yellow-vole planning → todo
- 2026-11-23T20:10:51Z golden-zinc-falcon todo → doing
- 2026-11-23T20:13:06Z golden-zinc-falcon: wrote the plan
- 2026-11-23T20:16:10Z golden-zinc-falcon: changed notes, summary
- 2026-11-23T20:18:10Z golden-zinc-falcon doing → review
- 2026-11-23T23:05:51Z friendly-coral-badger: changed notes; ticked acceptance criteria
- 2026-11-23T23:05:51Z friendly-coral-badger review → done
- 2026-11-25T18:32:36Z human: renumbered from TASK-YJ6VBS
