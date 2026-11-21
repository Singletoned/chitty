---
title: Reject criterion text containing any line break, with the single-line error
status: cold-read
labels:
  - bug
parent: TASK-376
created: 2026-11-21
---

## Description

Found 2026-11-21 in a cold read. `_criterion_text` in `src/chitty/model.py` rejects only `\n`, but `parse` splits lines with `str.splitlines`, which also breaks at `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, ` ` and ` ` (and `\r`). So `with_criteria(add=("a\x0cb",), ...)` gets past validation, and the re-parse in `_rebuild` raises a misleading `'## Acceptance Criteria' may only contain '- [ ] ...' items; found 'b'`. It should say `acceptance criterion must be a single line`, as it does for `\n`.

Change `_criterion_text` to reject text where `len(text.splitlines()) > 1`, or any of those characters, with the existing `acceptance criterion must be a single line` error. Nothing else changes.

Tests: in `tests/test_model.py` (or a new `tests/test_criterion_text.py`), for each of `\n`, `\r`, `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, ` ` and ` `, `with_criteria(add=(f"a{c}b",), remove=(), set_criteria=(), check=(), uncheck=())` on a parsed minimal ticket raises `TaskError` whose message is `acceptance criterion must be a single line`. Before the change every case except `\n` fails, because the message differs (record this in a note). `chitty edit --ac` goes through the same function, so no CLI change is needed.

## Acceptance Criteria

- [ ] Each of the ten line-break characters in a new criterion raises `TaskError("acceptance criterion must be a single line")`; every case but `\n` fails before the change (recorded in a note)
- [ ] `make check` passes

## History

- 2026-11-21T14:34:08Z sunny-ebony-kestrel → cold-read
- 2026-11-21T14:34:11Z sunny-ebony-kestrel: changed acceptance criteria
