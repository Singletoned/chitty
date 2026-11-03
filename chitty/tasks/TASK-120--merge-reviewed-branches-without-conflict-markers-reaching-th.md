---
title: Merge reviewed branches without conflict markers reaching the main checkout
status: todo
priority: high
created: 2026-11-03
---

## Description

The global `chitty` is an editable install of the main checkout, so a conflicted merge there leaves conflict markers in `src/chitty/*.py` and breaks `chitty` in every repository until it is resolved. Reviewers currently merge in the main checkout. Merge `main` into the ticket branch inside its worktree first, verify there, then fast-forward `main`. See `TASK-118`.

## Acceptance Criteria

- [ ] The guide tells reviewers to resolve conflicts in the ticket worktree and only fast-forward `main`
- [ ] The Pi review workflow follows the same order

## History

- 2026-11-03T11:39:03Z eager-raven → todo
