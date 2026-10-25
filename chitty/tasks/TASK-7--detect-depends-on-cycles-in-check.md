---
title: Detect depends_on cycles in check
status: done
labels:
  - check
created: 2026-10-25
---

## Description

chitty check should report each depends_on cycle once, naming every task in it. It currently catches only dangling references and self-dependency. Decided in HUMAN-1.

## Plan

Build a deterministic dependency graph from parsed tasks, identify each strongly connected component with more than one task, and report one problem for each participating task naming the complete cycle. Preserve current context/path output filtering.

## Notes

Question: How should overlapping simple cycles be reported once? Answer: treat each strongly connected component as one dependency cycle report; it names every mutually cyclic task and avoids duplicate noise.

Verified: the check graph reports the three-task cycle once per participating file, with all IDs named; make check passes.
