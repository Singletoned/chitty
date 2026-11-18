---
title: Stop `git._read_blobs` hanging on a few thousand objects
status: doing
labels:
  - bug
parent: TASK-376
created: 2026-11-18
---

## Description

`_read_blobs` in `src/chitty/git.py` writes every object ID to `git cat-file --batch` and closes its input before reading any output. Once both the object list and the output exceed the pipe buffers, `cat-file` blocks writing, Chitty blocks writing its input, and both wait forever. Cold reads on 2026-11-18 reproduced it on macOS (16 KB pipes; Linux has 64 KB): about 2,900 objects of 10-byte files hung, and 2,000 objects of 1 KB files; a `process.communicate` prototype read 5,000 1 KB objects in about 2 s. Today it is reached through `historical_files`; `TASK-378` keeps it for reading ticket files from ref tips, so every read in a repository with a few thousand tickets could hang.

Decisions:

- Feed the input without blocking the output: `process.communicate(input)` and parse the returned bytes, or write the input from a thread while reading. Keep the function's signature and results, including skipping `missing` objects and the `ChittyError`s for a bad header or a non-blob.
- Decode contents as today.

Tests: in `tests/test_git.py`, inheriting `RepoTestCase`, a repository with 5000 committed files of about 1 KB each (about 5 MB of output, well past any default pipe size), read through `_read_blobs` in one call in a subprocess (`sys.executable -c ...` with `timeout=20`), so a hang fails rather than stalls the suite. The test asserts that `chitty.git.__file__` lies under this checkout's `src`, so it tests this code, and compares every returned content with the file written. No property: the bug is a size threshold, shown by one large case; the existing tests cover the parsing.

## Acceptance Criteria

- [ ] `_read_blobs` returns all 5000 objects of the large case, each with the content written, within the 20 s timeout; the test fails (times out) before the change
- [ ] The existing `tests/test_git.py` tests pass unchanged, and `make check` passes

## Plan

Add a RepoTestCase regression test that creates and commits 5,000 approximately 1 KB files, invokes this checkout’s chitty.git._read_blobs in a subprocess with a 20-second timeout, and verifies every returned object and content. Run it against the current implementation to confirm the hang. Replace the sequential blocking pipe writes/reads in _read_blobs with subprocess.communicate(input=...), then parse its returned stdout using the existing cat-file batch framing and preserve missing-object, malformed-header, non-blob, decoding, and Git-failure behavior. Run the focused test, formatting, and make check; commit implementation and test with a Task: TASK-395 trailer, record verification, then set the ticket to review.

## History

- 2026-11-18T16:38:07Z lively-quartz-crane → backlog
- 2026-11-18T16:39:31Z lively-quartz-crane: changed title, labels, description, acceptance criteria
- 2026-11-18T16:39:31Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:46Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:45:09Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:45:09Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:45:11Z lively-quartz-crane planning → todo
- 2026-11-18T22:37:28Z zesty-russet-raven todo → doing
- 2026-11-18T22:38:30Z zesty-russet-raven: wrote the plan
