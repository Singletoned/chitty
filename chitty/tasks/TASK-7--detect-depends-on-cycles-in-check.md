---
title: Detect depends_on cycles in check
status: todo
labels:
  - check
created: 2026-10-25
---

## Description

chitty check should report each depends_on cycle once, naming every task in it. It currently catches only dangling references and self-dependency. Decided in HUMAN-1.
