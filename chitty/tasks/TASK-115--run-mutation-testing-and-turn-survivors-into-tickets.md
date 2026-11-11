---
title: Run mutation testing and turn survivors into tickets
status: backlog
priority: low
created: 2026-11-03
---

## Description

Mutation testing measures the tests rather than the code. Run `mutmut` or `cosmic-ray` occasionally over Chitty, not in `make check`, and file surviving mutants as "write a test that kills this" tickets. Start with the parser and transition code in `src/chitty/model.py` and `src/chitty/store.py`. The same run shows whether spec-first tests are stronger than older ones.

## History

- 2026-11-03T10:27:51Z lively-panda → backlog
- 2026-11-11T10:17:16Z vivid-yellowhammer: changed parent
