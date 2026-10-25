---
title: Stop chitty edit silently dropping repeated --note
status: todo
labels:
  - cli
  - bug
created: 2026-10-25
---

## Description

`chitty edit ID --note A --note B` keeps only B: click takes the last value of a non-multiple option, so A is lost without any error. Either make --note repeatable (each one a paragraph, in order) or reject repeats; silent loss is the bug. Check other single-value options for the same problem.
