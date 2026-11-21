---
title: Rewrite provisional ID mentions in a parsed ticket (`rewrite_task`)
status: cold-read
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-391` on 2026-11-21: the pure rewrite and its property are separable from the store method, which then calls this. `plan_renumbering` and `replace_ids` (`TASK-381`) are in `src/chitty/renumbering.py`.

Decisions:

- New pure function `rewrite_task(task: Task, mapping: Mapping[TaskId, TaskId]) -> Task` in `src/chitty/renumbering.py`: `replace_ids` on `title`, `depends_on`, `parent`, and every section except `History`, which is append-only (a ticket has no text before its first section: `_split_sections` in `src/chitty/model.py` rejects it); no other frontmatter field is rewritten (`labels`, `owner`, `priority`, `status`, `created`, `provisional`, `moved_from`); Acceptance Criteria per item in two calls, because a `set_criteria` item comes back unchecked and `with_section` refuses that section: `with_criteria(add=(), remove=(), set_criteria=<changed items>, check=(), uncheck=())`, then `with_criteria(add=(), remove=(), set_criteria=(), check=<indices checked before>, uncheck=())`. (`TASK-380` adds `provisional` to `FIELD_ORDER`, so `with_field("provisional", None)` works.) `moved_from` is not rewritten, so a renumbered file's own `moved_from` and History keep the provisional ID.
- Out of scope: files, Git and `Repo` (that is `TASK-391`).

Tests: a Hypothesis property in `tests/test_property_renumbering.py` (`TASK-381`'s file). Generate a `Task` built through the model and rendered once with `render()`, so the input is canonical. It mentions old IDs in `title`, `depends_on`, `parent`, `Description`, each Acceptance Criteria item (some checked), `Notes`, optionally `Plan` and `Summary` (the parser accepts only the names in `SECTION_ORDER`, `src/chitty/model.py`), and `History`. Generated criterion text must be text `with_criteria` accepts (it goes through `_criterion_text`). Properties: every non-History mention of a mapped ID is rewritten; the rendered `History` section is byte-identical; each criterion keeps its checked state; and with an identity mapping the rendered output equals the input. Text includes near misses built from the drawn ID (for it, `<ID>A` and `X<ID>`), which stay unchanged, and mentions inside code spans and URLs, which are rewritten (they match `TASK-381`'s rule). First add `rewrite_task` raising `NotImplementedError`, so the property fails before the change.

## Acceptance Criteria

- [ ] The `rewrite_task` property passes, and fails against the `NotImplementedError` stub (recorded in a note)
- [ ] `make check` passes

## History

- 2026-11-21T13:10:17Z sunny-ebony-kestrel → planning
- 2026-11-21T13:11:03Z sunny-ebony-kestrel planning → cold-read
