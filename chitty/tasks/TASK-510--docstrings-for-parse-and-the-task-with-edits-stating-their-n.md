---
title: Docstrings for `parse` and the `Task.with_*` edits, stating their normalisations
status: review
labels:
  - untestable
owner: nimble-umber-adder
parent: TASK-376
created: 2026-11-21
---

## Description

Document the existing behavior of `parse`, `Task.section`, `Task.with_field`, `Task.with_section`, and `Task.with_criteria` in `src/chitty/model.py`. These contracts were difficult to establish when planning `TASK-507`. Change only docstrings; do not change behavior or add tests for wording. Run `make check` to verify the repository still passes.

- `parse`: document validation failures and their `TaskError` message prefixes, including line-number prefixes where present. Cover line endings, frontmatter, section structure, acceptance criteria, History, and required Description. `SECTION_ORDER` supplies known section names and guides insertion, not validation of their relative order: parsing preserves input order, except that `History`, if present, must be last. Distinguish malformed History entries from invalid dates or timestamps.
- `Task.section`: returns content without the heading, stripping edge newline characters but not spaces or tabs, or `None` if absent.
- `Task.with_field`: accepts keys in `FIELD_ORDER` and revalidates the result. `None` or `[]` requests removal, except `provisional` accepts only `True` or `None`; required keys cannot be removed. Duplicate entries in `labels` and `depends_on` raise.
- `Task.with_section`: refuses Acceptance Criteria; trims input edge newlines and trailing whitespace on each line, and inserts blank separators when writing. Empty or whitespace-only text requests removal, but Description must remain nonempty. Document rejection of carriage returns and edits that would change section boundaries.
- `Task.with_criteria`: takes 1-based indices into the original list and rejects conflicting operations for an index. It validates replacements and additions before editing; in original order it skips removals, replaces text, and applies checkbox updates on their respective items, then appends additions. A replacement becomes a single unchecked `- [ ]` line, discarding the old marker (including `[X]`) and continuation lines. Added and replacement text is stripped and must be nonempty and single-line.

## Plan

Trace `parse` and its validation helpers, then document their rejection rules and error prefixes. Read each edit helper and document its normalization, ordering, and errors without changing behavior. Run `chitty fix`, `make format`, and `make check` before handing off for review.

## Notes

The requested `parse` rejection for sections out of `SECTION_ORDER` does not exist. In `src/chitty/model.py`, `_split_sections` uses `SECTION_ORDER` to recognize names but preserves input order, while `_parse_history` alone requires `History` to be last. Verified in the worktree: `Notes` before `Description` parses and round-trips unchanged; putting `History` before `Description` raises `'## History' must be the last section`. The planner should replace the general order requirement with the History-only rule to keep this docs-only, or split any intended order enforcement into a separate behavior change.

The helper descriptions also need precise limits: `section` uses `strip("\n")`, so space- or tab-only edge lines are not stripped. `with_field` checks `provisional` before the removal branch, so it accepts `True` or `None` but rejects `[]`; removing a required key also fails on reparse. `with_section` uses `rstrip()` (not just spaces and tabs), trims input edge newlines and adds section separators, and treats whitespace-only input as a removal request, but `Description` cannot be removed. For `with_criteria`, distinguish validation from output order: it validates replacements before additions, then walks the original items (skip removed, replace text, update checkbox as applicable), then appends additions; conflicting operations on one original index raise. These should be documented as implemented. No docstrings were changed and `make check` was not run.

## Summary

Added docstrings for `parse`, `Task.section`, `Task.with_field`, `Task.with_section`, and `Task.with_criteria` in `src/chitty/model.py`. The parser docs spell out the error prefixes and clarify that `History` must be last but other sections need not follow `SECTION_ORDER`. The edit docs state normalization, removal exceptions, and criterion operation order. No behavior changed: the module AST is identical after removing docstrings. `make format`, `git diff --check`, and `make check` passed (972 tests). No follow-ups needed.

## History

- 2026-11-21T14:32:03Z sunny-ebony-kestrel → todo
- 2026-11-21T15:46:49Z nimble-umber-adder: changed owner; wrote the plan
- 2026-11-21T15:46:49Z nimble-umber-adder todo → doing
- 2026-11-21T15:47:19Z nimble-umber-adder: changed owner, notes
- 2026-11-21T15:47:19Z nimble-umber-adder doing → planning
- 2026-11-21T15:50:50Z nimble-umber-adder: changed owner, description
- 2026-11-21T15:50:50Z nimble-umber-adder planning → todo
- 2026-11-21T15:50:54Z nimble-umber-adder: changed owner
- 2026-11-21T15:50:54Z nimble-umber-adder todo → doing
- 2026-11-21T15:54:35Z nimble-umber-adder: changed summary
- 2026-11-21T15:54:35Z nimble-umber-adder doing → review
