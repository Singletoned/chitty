---
title: Edit one criterion's text without losing its checked state or the other items' formatting
status: planning
parent: TASK-376
created: 2026-11-21
---

## Description

`Task.with_criteria` (`src/chitty/model.py`) writes a `set_criteria` item as a single unchecked `- [ ]` line, so callers that only want to change an item's text must call it twice: once to set the text and once to check the item again. `rewrite_task` in `src/chitty/renumbering.py` does exactly that, and on 2026-11-21 planning it took several rounds to discover this behaviour. A method that does the one thing removes the dance.

Decisions:

- New `Task.with_criterion_text(index: int, text: str) -> Task` in `src/chitty/model.py`. `index` is 1-based, as in `with_criteria`. It replaces item `index`'s text, keeps its checked state and marker character (`[ ]`, `[x]` or `[X]` as written), and writes the item as one line, so its continuation lines are replaced. Every other item, and everything else in the section, keeps its exact bytes. Text is validated as `with_criteria` validates set text: multi-line or empty text raises `TaskError`, and so does an index out of range.
- `rewrite_task` uses it, one call per changed criterion, in place of its two `with_criteria` calls.
- Out of scope: `chitty edit --set-ac` (`TaskEdit` in `src/chitty/store.py` passes `set_criteria` to `with_criteria`), which still unticks the item it sets. Whether it should keep the checked state is a separate decision.

Tests: Hypothesis properties in a new `tests/test_property_criterion_text.py`, using `ticket_texts` from `tests/ticket_strategies.py` (filtered to tickets with at least one criterion) to get a parsed `task`, a drawn valid index, and drawn single-line non-empty text. Properties: (1) `parse(result.render())` has the new text at `index`, and the same `checked` value as before; (2) the item's marker character is unchanged; (3) every other criterion's rendered lines, and every other section's rendered lines, are byte-identical to `task.render()`'s; (4) the criteria count is unchanged. A unit test asserts that `TaskError` is raised for index 0, for an index past the end, for empty text and for text containing `\n`. First add the method raising `NotImplementedError` and record the properties failing. Existing `rewrite_task` properties in `tests/test_property_renumbering.py` must still pass unchanged.

## History

- 2026-11-21T14:32:56Z sunny-ebony-kestrel → planning
