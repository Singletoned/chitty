---
title: Give each chitty repo a project name registered in the inbox
status: todo
labels:
  - config
depends_on:
  - TASK-24
parent: TASK-25
created: 2026-10-27
---

## Description

Each repo has a project name in its config; the inbox folder records which names exist and which repo, if any, each belongs to.

## Acceptance Criteria

- [ ] Config key project = "name"; chitty init writes it, defaulting to the directory name; names follow sump's slug rules (lowercase letters, digits, . _ -, starting and ending with a letter or digit), otherwise a config error
- [ ] chitty init and chitty pull register the project in ~/.local/share/chitty/inbox/<name>/, recording the repo path
- [ ] A name already registered to a different repo path is an error asking for an explicit project = name
- [ ] Registering a name created with suggest --create (no repo yet) claims it for this repo and keeps its waiting suggestions
- [ ] Inbox location follows XDG_DATA_HOME; tests use a temp dir
- [ ] Tests, PLAN.md and README updated
