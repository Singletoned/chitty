---
title: Clarify how `mate release` distinguishes patch from minor
status: todo
priority: high
created: 2026-11-01
---

## Description

TASK-80 defines a minor release as a second `chitty init` changing an isolated repo after the last release init. Current `init` always updates `chitty_version` to the running version, so that second invocation always changes the file and every release becomes minor. Decide whether release classification must ignore `chitty_version`, compare only the guide/config shape, or use another rule.

## History

- 2026-11-01 → todo
