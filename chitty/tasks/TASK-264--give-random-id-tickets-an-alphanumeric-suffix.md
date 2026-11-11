---
title: Give random-ID tickets an alphanumeric suffix
status: backlog
depends_on:
  - TASK-263
parent: TASK-262
created: 2026-11-11
---

## Description

- `random_ids` contexts draw a number from 10000000 to 99999999 (`_random_number` in `src/chitty/store.py`). Draw eight upper-case letters and digits instead, with at least one letter, for example `BACKLOG-K3F9X2AB`.
- Existing numeric `BACKLOG-` tickets keep their IDs.

## History

- 2026-11-11T11:35:13Z vivid-yellowhammer → backlog
- 2026-11-11T13:43:24Z vivid-yellowhammer: changed description
