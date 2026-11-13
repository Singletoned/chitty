---
title: Report all missing run configuration before starting
status: backlog
created: 2026-11-13
---

## Description

When `chitty run` starts, preflight every required `chitty.toml` field and report all missing values in one error. This repository first failed on missing `setup = "make install"`, then on missing `check = "make check"`; sequential validation caused two avoidable failed invocations. Include example configuration for each missing field.

## Notes

Suggestion origin: injustice-league

## History

- 2026-11-13T14:02:36Z zesty-umber-puffin → backlog
- 2026-11-13T14:02:37Z zesty-umber-puffin: changed notes
