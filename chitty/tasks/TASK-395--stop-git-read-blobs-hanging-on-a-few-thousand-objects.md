---
title: Stop `git._read_blobs` hanging on a few thousand objects
status: cold-read
labels:
  - bug
parent: TASK-376
created: 2026-11-18
---

## Description

`_read_blobs` in `src/chitty/git.py` writes every object ID to `git cat-file --batch` and closes its input before reading any output. Once the output exceeds the pipe buffer, `cat-file` blocks writing, Chitty blocks writing its input, and both wait forever. A cold read on 2026-11-18 reproduced it in a scratch repository: 3000 ticket objects hung (killed after 20 s), 2000 finished. Today it is reached through `historical_files`; `TASK-378` keeps it for reading ticket files from ref tips, so every read in a repository with a few thousand tickets could hang.

Decisions:

- Feed the input without blocking the output: `process.communicate(input)` and parse the returned bytes, or write the input from a thread while reading. Keep the function's signature and results, including skipping `missing` objects and the `ChittyError`s for a bad header or a non-blob.
- Decode contents as today.

Tests: in `tests/test_git.py`, inheriting `RepoTestCase`, a repository with 5000 committed small files read through `_read_blobs` in one call, with a timeout (for example by running it in a subprocess with `timeout=60`) so a hang fails rather than stalls the suite. No property: the bug is one size threshold, shown by one large case; the existing tests cover the parsing.

## Acceptance Criteria

- [ ] `_read_blobs` returns all 5000 objects of the large case with their contents and finishes within the timeout; the test fails (times out) before the change
- [ ] The existing `tests/test_git.py` tests pass unchanged, and `make check` passes

## History

- 2026-11-18T16:38:07Z lively-quartz-crane → backlog
- 2026-11-18T16:39:31Z lively-quartz-crane: changed title, labels, description, acceptance criteria
- 2026-11-18T16:39:31Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:46Z lively-quartz-crane planning → cold-read
