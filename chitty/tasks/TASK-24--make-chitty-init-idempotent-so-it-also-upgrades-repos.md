---
title: Make chitty init idempotent so it also upgrades repos
status: done
labels:
  - cli,config
created: 2026-10-27
---

## Description

chitty init refuses to run where chitty.toml exists. Make it safe to run any number of times: on a new repo it sets everything up as now; on an existing one it adds only what is missing, so it doubles as the upgrade step when new config options are introduced. It never changes a value that is already set.

## Acceptance Criteria

- [x] Running init twice changes nothing the second time and says so
- [x] On an existing repo, init adds missing config keys with explicit values, leaving existing keys, values and comments untouched (chitty.toml or [tool.chitty] in pyproject.toml, whichever is in use)
- [x] Creates missing context directories; replaces the chitty block in AGENTS.md with the current one, or adds it if absent
- [x] Reports each change it made
- [x] --prefix that disagrees with an existing default context's prefix is an error, not a rewrite
- [x] Tests, PLAN.md, README and init --help updated

## Plan

Inspect init and configuration migration requirements, then make init safely add missing Chitty files/guide/config defaults without overwriting existing user configuration, with focused regression tests.

## Notes

Init now safely upgrades Chitty config/AGENTS/task directories, reports updates or no-op, protects explicit prefix choices, and covers chitty.toml plus pyproject configuration. Full make check passes.
