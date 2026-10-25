---
title: Allow configuring chitty in pyproject.toml
status: todo
labels:
  - config
created: 2026-10-25
---

## Description

Read the repo config from a [tool.chitty] table in pyproject.toml as an alternative to chitty.toml. Root discovery currently looks only for chitty.toml; decide what happens when both exist (probably an error).
