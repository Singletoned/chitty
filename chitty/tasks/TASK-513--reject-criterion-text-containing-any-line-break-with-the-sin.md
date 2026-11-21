---
title: Reject criterion text containing any line break, with the single-line error
status: doing
labels:
  - bug
parent: TASK-376
created: 2026-11-21
---

## Description

Found 2026-11-21 in a cold read. `_criterion_text` in `src/chitty/model.py` rejects only `\n`, but `parse` splits lines with `str.splitlines`, which also breaks at `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `\u2028` and `\u2029` (and `\r`). So `with_criteria(add=("a\x0cb",), ...)` gets past validation, and the re-parse in `_rebuild` raises a misleading `'

## Acceptance Criteria

- [ ] Each of the ten line-break characters in a new criterion raises `TaskError("acceptance criterion must be a single line")`; every case but `\n` fails before the change (recorded in a note)
- [ ] `make check` passes

## Notes

Planner 2026-11-21: the last two characters are U+2028 and U+2029, written here as the escapes `\u2028` and `\u2029` (an earlier version held the raw characters by mistake). Fails-before check, probed: `\n` already gives the single-line error; the other nine, including `\r`, give a different message today. Out of scope, same bug class: `_check_single_line` and `render_scalar` in `src/chitty/model.py` also check only `\n`.

## History

- 2026-11-21T14:34:08Z sunny-ebony-kestrel → cold-read
- 2026-11-21T14:34:11Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T14:36:10Z sunny-ebony-kestrel: changed description, notes
- 2026-11-21T14:36:10Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T15:24:28Z upbeat-fawn-lapwing todo → doing
