---
title: Docstrings for `parse` and the `Task.with_*` edits, stating their normalisations
status: todo
labels:
  - untestable
owner: untestable
parent: TASK-376
created: 2026-11-21
---

## Description

On 2026-11-21 `TASK-507` went through many planning rounds because these functions' normalisations and errors were not written down. In `src/chitty/model.py`, give `parse` a docstring, and extend those of `Task.section`, `Task.with_field`, `Task.with_section` and `Task.with_criteria`. Check each statement against the code as it is when you write it (do not copy this list):

- `parse`: what it rejects, with the error's start. At least: text with `\r`, text not ending in `\n`, content before the first `##` section, a `#` heading, an unknown section name, sections out of `SECTION_ORDER`, a missing or empty `Description`, and a malformed `History` line.
- `section`: it strips leading and trailing blank lines.
- `with_field`: which keys it accepts, that `None` or `[]` removes, and that a list with duplicates raises.
- `with_section`: it refuses Acceptance Criteria, strips trailing spaces and tabs from every line, normalises blank lines around the section, and removes the section when given empty text.
- `with_criteria`: the order it applies `add`, `remove`, `set_criteria`, `check` and `uncheck`; that a re-set item is written as one `- [ ]` line, so its checked state and any `[X]` or continuation lines are lost; and that multi-line text raises.

Do not change behaviour. `make check` passes.

## History

- 2026-11-21T14:32:03Z sunny-ebony-kestrel → todo
