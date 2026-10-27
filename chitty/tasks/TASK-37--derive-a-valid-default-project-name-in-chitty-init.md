---
title: Derive a valid default project name in chitty init
status: todo
labels:
  - bug,config
created: 2026-10-27
---

## Description

init uses the directory name verbatim as project, so a directory such as MyProject or empty.wpWx fails with 'chitty.toml: project: must use lowercase letters…' naming a chitty.toml that was never written. The name is also interpolated into TOML without escaping, so a quote in a directory name would break the file.

## Acceptance Criteria

- [ ] The default project is the directory name lowercased with characters outside the slug rules replaced by '-', and leading/trailing non-alphanumerics stripped
- [ ] If nothing valid remains, init fails with a message saying to set project = "name" (and how), without naming a file that does not exist
- [ ] Values written into TOML are properly escaped
- [ ] Regression tests fail before the fix

## History

- 2026-10-27 → todo
