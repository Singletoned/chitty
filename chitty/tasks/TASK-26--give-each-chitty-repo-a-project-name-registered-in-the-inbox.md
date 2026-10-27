---
title: Give each chitty repo a project name registered in the inbox
status: done
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

- [x] Config key project = "name"; chitty init writes it, defaulting to the directory name; names follow sump's slug rules (lowercase letters, digits, . _ -, starting and ending with a letter or digit), otherwise a config error
- [x] chitty init and chitty pull register the project in ~/.local/share/chitty/inbox/<name>/, recording the repo path
- [x] A name already registered to a different repo path is an error asking for an explicit project = name
- [x] Registering a name created with suggest --create (no repo yet) claims it for this repo and keeps its waiting suggestions
- [x] Inbox location follows XDG_DATA_HOME; tests use a temp dir
- [x] Tests, PLAN.md and README updated

## Plan

Add validated project names to repository configuration, register them in an XDG-data inbox directory during init, and cover ownership/collision behavior with temp-data tests.

## Notes

Added validated optional project config, XDG data inbox registration/ownership protection, init registration and upgrade behavior, isolated XDG test setup, plus docs and regression coverage. Full make check passes.
