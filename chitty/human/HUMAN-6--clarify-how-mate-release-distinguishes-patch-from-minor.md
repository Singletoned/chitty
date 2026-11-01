---
title: Clarify how `mate release` distinguishes patch from minor
status: done
priority: high
created: 2026-11-01
---

## Description

TASK-80 defines a minor release as a second `chitty init` changing an isolated repo after the last release init. Current `init` always updates `chitty_version` to the running version, so that second invocation always changes the file and every release becomes minor. Decide whether release classification must ignore `chitty_version`, compare only the guide/config shape, or use another rule.

## Notes

Decided by the human (2026-11-01): release classification ignores the `chitty_version` line. A release is minor when `init` from this checkout changes anything else in a repository set up by the last release's `init`, otherwise patch.

Reviewed: the decision came from the human in conversation and is recorded on TASK-80.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → review
- 2026-11-01 review → done
