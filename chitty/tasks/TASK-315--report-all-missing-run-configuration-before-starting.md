---
title: Report all missing run configuration before starting
status: doing
created: 2026-11-13
---

## Description

When `chitty run` starts, preflight every required `chitty.toml` field and report all missing values in one error. This repository first failed on missing `setup = "make install"`, then on missing `check = "make check"`; sequential validation caused two avoidable failed invocations. Include example configuration for each missing field.

## Acceptance Criteria

- [ ] When multiple static run settings are missing, `chitty run` fails before setup, ticket selection, or agent launch and reports every missing setting in one error, with an example configuration line for each; the regression fails against the current implementation.
- [ ] The preflight still reports the correct `chitty.toml` or `pyproject.toml` source and preserves existing validation for invalid or incomplete agent commands.
- [ ] The `chitty run` documentation describes the required configuration and shows example values for every preflight setting.

## Plan

Update run preflight to collect every missing required setting before raising, preserving the selected config source and including a concrete TOML example for each setting. Add a regression test that removes multiple required settings and asserts one error lists all of them and their examples, then update the runner documentation to describe the preflight and configuration examples. Run the regression against the current implementation first, then format and full checks.

## Notes

Suggestion origin: injustice-league

## History

- 2026-11-13T14:02:36Z zesty-umber-puffin → backlog
- 2026-11-13T14:02:37Z zesty-umber-puffin: changed notes
- 2026-11-13T14:03:18Z zesty-umber-puffin: changed acceptance criteria; wrote the plan
- 2026-11-13T14:03:18Z zesty-umber-puffin backlog → doing
