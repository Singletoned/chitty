---
title: Find what leaves temporary projects in the real inbox
status: doing
labels:
  - bug
priority: low
parent: TASK-106
created: 2026-11-04
---

## Description

`~/.local/share/chitty/inbox` holds `chitty-run-txsmwm`, `chitty-task-123-tlk9qr`, `prj`, `repo`, `t45`, and several `tmp-*` directories, seen on 2026-11-04. They look like temporary repositories, so something registered them outside a test's temporary `XDG_DATA_HOME`. It may be a test that does not inherit `RepoTestCase`, or an agent's hand trial of `chitty init` in a scratch repository. `chitty init` registers a project without asking. They do no harm beyond appearing as known projects in `chitty suggest`'s errors.

The cold read found most of the cause from each directory's `repo` owner file: `tmp-*`, `t45`, `chitty-task-123-tlk9qr` and `chitty-run-txsmwm` point at scratch directories, so they were hand trials of `chitty init`. `repo` matches the layout of `RepoTestCase`, and `prj` has an empty owner file, so those two may be tests, both from about 1 November. Compare a listing of the real inbox before and after a full test run. Fix any test that changes it, and record the result. Removing the directories is for the human, so list them in the note.

## Acceptance Criteria

- [ ] A note records the before and after listing of the real inbox around a full test run, and what caused each directory

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. It found the likely cause, and the check now names how to show it.

## History

- 2026-11-04T21:00:17Z mellow-newt → backlog
- 2026-11-04T21:01:56Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T21:01:57Z mellow-newt backlog → todo
- 2026-11-06T00:28:18Z youthful-crane todo → doing
