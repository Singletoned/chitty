---
title: Let a repository declare paths ticket branches must not change
status: planning
created: 2026-11-16
---

## Description

`_prepare_review` in `src/chitty/run.py` already fails a review when the branch changes the Chitty config or the managed `AGENTS.md` block. This repository also forbids branches changing `__version__` in `src/chitty/__init__.py`, which caused the 56-failure loop on `TASK-179`, and only prose enforces it. Let a repository list further protected paths in its Chitty config, checked the same way at review, then remove the `__version__` rule from `AGENTS.md`. Planning decides whether whole files are enough or a line pattern is needed.

## History

- 2026-11-16T09:59:55Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:37Z intrepid-coral-raven backlog → planning
- 2026-11-16T10:50:31Z intrepid-coral-raven: changed title, description
