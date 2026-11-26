---
title: A stale inbox repo path makes every command fail with Not a directory
status: doing
labels:
  - bug
priority: medium
created: 2026-11-25
moved_from: TASK-AZ59M3
---

## Description

Seen 2026-11-25. Each project's inbox records its repository in `~/.local/share/chitty/inbox/<project>/repo`. A worker-trial clone was deleted, and a later clone reused the project name. Every command in the new clone, starting with `chitty run`, failed with `Error: Not a directory: <old deleted path>`. It comes from `is_repository` (`src/chitty/git.py`), reached through `register_project` -> `_same_git_repository` -> `git_common_dir(Path(current))` in `src/chitty/config.py`. The message does not say the path came from the inbox, so it was hard to trace; the fix was deleting the entry by hand.

Change, in `register_project`: when the recorded path is not an existing directory, record the new `root` instead, and print `warning: project <name> was registered to <old>, which no longer exists; registered <new> instead` on stderr, as `store.py` prints its other warnings. A recorded path that exists keeps today's behaviour (same repository allowed, another repository refused). With `root` `None` (suggesting from outside a repository), leave the stale path alone, as today.

No property test: one stale-path case and one regression case, both listed.

Related: TASK-50 (list and prune stale registrations). Out of scope here.

## Acceptance Criteria

- [ ] A test (inheriting `RepoTestCase`) records a project's inbox `repo` file as a directory that no longer exists, then runs `chitty inbox --pull` in a repository with that project name: it exits 0, the `repo` file now holds this repository's resolved path, and stderr has `warning: project <name> was registered to <old path>, which no longer exists; registered <new path> instead`. Fails today with `Not a directory: <old path>`.
- [ ] Regression tests: a recorded path that still exists and belongs to another repository still refuses with `is registered to`; `tests/test_inbox.py` and `tests/test_property_inbox.py` pass; `make check` passes.

## History

- 2026-11-25T22:28:31Z calm-ochre-quail → backlog
- 2026-11-25T22:28:33Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:18Z calm-ochre-quail: changed labels, notes
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-AZ59M3
- 2026-11-26T00:21:46Z calm-ochre-quail: replaced notes; changed priority, description, acceptance criteria
- 2026-11-26T00:21:46Z calm-ochre-quail backlog → planning
- 2026-11-26T00:21:51Z calm-ochre-quail planning → cold-read
- 2026-11-26T00:22:59Z calm-ochre-quail cold-read → todo
- 2026-11-26T00:40:30Z zesty-jade-wren todo → doing
