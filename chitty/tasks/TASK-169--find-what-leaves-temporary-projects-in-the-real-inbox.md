---
title: Find what leaves temporary projects in the real inbox
status: backlog
labels:
  - bug
priority: low
parent: TASK-106
created: 2026-11-04
---

## Description

`~/.local/share/chitty/inbox` holds `chitty-run-txsmwm`, `chitty-task-123-tlk9qr`, `prj`, `repo`, `t45`, and several `tmp-*` directories, seen on 2026-11-04. They look like temporary repositories, so something registered them outside a test's temporary `XDG_DATA_HOME`. It may be a test that does not inherit `RepoTestCase`, or an agent's hand trial of `chitty init` in a scratch repository. `chitty init` registers a project without asking. They do no harm beyond appearing as known projects in `chitty suggest`'s errors.

Find the cause from the code and directory timestamps, fix it if it is a test, and say in a note if it was hand trials. Removing the directories is for the human, so list them in the note.

## Acceptance Criteria

- [ ] A note says what caused them, and if a test did, a test run leaves the real inbox unchanged

## History

- 2026-11-04T21:00:17Z mellow-newt → backlog
