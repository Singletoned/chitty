---
title: Derive a valid default project name in chitty init
status: done
labels:
  - bug,config
created: 2026-10-27
---

## Description

init uses the directory name verbatim as project, so a directory such as MyProject or empty.wpWx fails with 'chitty.toml: project: must use lowercase letters…' naming a chitty.toml that was never written. The name is also interpolated into TOML without escaping, so a quote in a directory name would break the file.

## Acceptance Criteria

- [x] The default project is the directory name lowercased with characters outside the slug rules replaced by '-', and leading/trailing non-alphanumerics stripped
- [x] If nothing valid remains, init fails with a message saying to set project = "name" (and how), without naming a file that does not exist
- [x] Values written into TOML are properly escaped
- [x] Regression tests fail before the fix

## Plan

Add failing init tests for normalized, empty, and TOML-special directory names. Centralize valid default-project derivation and TOML string rendering, use them for new and upgraded configuration, then run make check and verify all criteria.

## Notes

Ready for review: make check passes.

## Summary

init now derives normalized project names, rejects empty names before creating a configuration, and renders added TOML strings with JSON-compatible escaping. Verified with make check (134 tests).

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
