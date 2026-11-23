---
title: Run `git log` for `Task:` trailer commits
status: planning
depends_on:
  - TASK-358
created: 2026-11-23
provisional: true
---

## Description

Split from `TASK-358` on 2026-11-23 after its third cold read. `TASK-358` adds `TrailerCommit`, `TRAILER_LOG_OPTIONS` and the pure `parse_trailer_log` in `src/chitty/git.py`; this ticket runs `git log` and feeds them. `TASK-571` calls it from `chitty check`.

Decision, in `src/chitty/git.py`: new `trailer_commits(root: Path, ref: str) -> list[TrailerCommit]`. One `git log <ref>` call with `TRAILER_LOG_OPTIONS`, run with `subprocess.run(check=False, cwd=root, capture_output=True)` as `changed_paths` does: stdout is bytes (not `text=True`, which rewrites `\r`). A non-zero exit raises `ChittyError` naming the command and `root`, with Git's stderr, as `changed_paths` does. Stdout is decoded as UTF-8; a `UnicodeDecodeError` is raised as `ChittyError` naming the ref, so a non-UTF-8 path fails loudly. The text goes to `parse_trailer_log`; the result is newest first, as Git prints. Why the options: `--no-renames`, so a file moved from `src/` into `chitty/tasks/` lists both paths; `--root`, `--no-show-signature` and `--encoding=UTF-8`, so user config (`log.showRoot`, `log.showSignature`, `i18n.logOutputEncoding`) cannot change the bytes. Nothing calls `trailer_commits` yet.

Tests: examples with real Git in `tests/test_trailer_commits.py` (added by `TASK-358`), in a temp repository on branch `main`. No property: the parser's properties are in `TASK-358`; this is the wiring to one external process, a fixed set of cases.

- Three commits: the root, with subject `Add ü` and two `Task:` trailers, changing `src/a.py` and `src/b\rc.py`; one whose only path is `chitty/tasks/TASK-1 ü "q".md`; one with subject `chitty: edit TASK-1` and no change (`--allow-empty`). Assert the bytes `git log main` prints with `TRAILER_LOG_OPTIONS` equal the layout `TASK-358` describes, built in the test from the known SHAs, and that `trailer_commits(root, "main")` returns the three commits field by field.
- Config: set `log.showSignature=true`, `i18n.logOutputEncoding=ISO-8859-1` and `log.showRoot=false` in that repository; `trailer_commits` returns the same commits. (Without `--root`, `log.showRoot=false` drops the root commit's paths.)
- Non-UTF-8: add a commit whose tree holds a path with byte `\xff`, built with `git mktree` and `git commit-tree` (some file systems refuse such names); `trailer_commits` raises `ChittyError`.
- Unknown ref: `trailer_commits(root, "nope")` raises `ChittyError` whose message contains `git log` and the root.

## Acceptance Criteria

- [ ] The three-commit example passes: the exact `git log` bytes match the layout and `trailer_commits` returns the three commits field by field
- [ ] The config, non-UTF-8 and unknown-ref tests pass; each fails when the matching handling is removed (drop `--root`, decode with `errors="replace"`, use `check=True`). Record those runs in a note
- [ ] `make check` passes

## Notes

Planner, 2026-11-23: kept in `planning` because it uses `TrailerCommit`, `TRAILER_LOG_OPTIONS` and `parse_trailer_log` from `TASK-358`, not yet built. When `TASK-358` is `done`, compare with what landed, cold-read, then move to `todo`.

## History

- 2026-11-23T18:39:16Z witty-yellow-vole → planning
