---
title: Allow configuring chitty in pyproject.toml
status: done
labels:
  - config
created: 2026-10-25
---

## Description

Read the repo config from a [tool.chitty] table in pyproject.toml as an alternative to chitty.toml. Root discovery currently looks only for chitty.toml; decide what happens when both exist (probably an error).

## Plan

Introduce one resolver for the active repository configuration source, use it for discovery and loading, accept [tool.chitty] in pyproject.toml, and reject simultaneous Chitty config sources as ambiguous. Add focused compatibility and discovery tests.

## Notes

Question: Does an unrelated pyproject.toml count as a competing config? Answer: no—only a pyproject.toml containing [tool.chitty] is a Chitty source; when both actual sources exist, reject the ambiguity.

Verified: legacy chitty.toml and pyproject [tool.chitty] configurations load and discover correctly; an unrelated pyproject is ignored and two actual sources are rejected. make check passes.
