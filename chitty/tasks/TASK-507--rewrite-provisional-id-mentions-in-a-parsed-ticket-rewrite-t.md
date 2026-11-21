---
title: Rewrite provisional ID mentions in a parsed ticket (`rewrite_task`)
status: doing
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-391` on 2026-11-21: the pure rewrite and its property are separable from the store method, which then calls this. `plan_renumbering` and `replace_ids` (`TASK-381`) are in `src/chitty/renumbering.py`.

Decisions:

- New pure function `rewrite_task(task: Task, mapping: Mapping[TaskId, TaskId]) -> Task` in `src/chitty/renumbering.py`: `replace_ids` on `title`, `depends_on`, `parent`, and every section except `History`, which is append-only (a ticket has no text before its first section: `_split_sections` in `src/chitty/model.py` rejects it); no other frontmatter field is rewritten (`labels`, `owner`, `priority`, `status`, `created`, `provisional`, `moved_from`); Acceptance Criteria per item in two calls, because a `set_criteria` item comes back unchecked and `with_section` refuses that section: `with_criteria(add=(), remove=(), set_criteria=<changed items>, check=(), uncheck=())`, then `with_criteria(add=(), remove=(), set_criteria=(), check=<indices checked before>, uncheck=())`. (Clearing `provisional` on a renumbered ticket is `TASK-391`'s job, not this function's.) `moved_from` is not rewritten, so a renumbered file's own `moved_from` and History keep the provisional ID.
- Set `title`, `parent` and `depends_on` with `Task.with_field` (`src/chitty/model.py`). Never run `replace_ids` over rendered text, which would also touch `labels`, `owner` and History.
- Call `with_section` only for a section whose `replace_ids` output differs from its current text; `with_section` normalises blank lines, so an untouched section must not be re-set. With an empty mapping nothing is re-set.
- Mentions follow `replace_ids` exactly (`TASK-381`): an ID followed by `-` (`TASK-1-foo`) is a mention and is rewritten; an ID preceded by a letter, digit or `-` (`XTASK-1`, `X-TASK-1`) or followed by a letter or digit (`TASK-1A`) is not.
- Out of scope: files, Git and `Repo` (that is `TASK-391`).

Tests: Hypothesis properties in `tests/test_property_renumbering.py` (`TASK-381`'s file). Generate ticket text and `parse` it (`src/chitty/model.py`) to get the input `task`; compare outputs with `render()`. Constraints that keep the text valid: the title and each criterion are single-line; no section text line starts with `#` heading syntax or is a setext underline (`---` or `===` after a paragraph); sections are `Description`, `Acceptance Criteria`, `Notes`, optionally `Plan` and `Summary`, and `History` (the parser accepts only the names in `SECTION_ORDER`). Mention generated IDs in `title`, `depends_on`, `parent`, every section, each criterion (some checked), and also `labels`, `owner` and `moved_from`. Generate an injective mapping (distinct keys map to distinct targets, as `plan_renumbering` guarantees) that covers some of those IDs but not others, and sometimes chains (`{A: B, B: C}`). Generated frontmatter uses only values `parse` accepts (valid `status`, `created`, and `labels` and `owner` in the format `_render_field` writes); the `tasks` strategy in `tests/test_check_edit.py` shows one way. A draw that `parse` rejects is a test bug, not something to `assume` away. Properties: (1) for `title`, `parent` and each `depends_on` entry the result equals `replace_ids(<old value>, mapping)`, and for every non-History section `rewritten.section(name) == replace_ids(task.section(name), mapping)` (parsed text, not bytes), so each mention becomes its image in one pass (with `{A: B, B: C}`, `A` becomes `B`, never `C`); (2) an unmapped ID, and the near misses `<ID>A`, `X<ID>` and `X-<ID>` built from a drawn ID, stay unchanged, while `<ID>-x` is rewritten; (3) the rendered `History` section, `labels`, `owner`, `moved_from` and every other frontmatter field are byte-identical; (4) each criterion keeps its checked state; (5) with an empty mapping, `rewrite_task(task, {}).render() == task.render()`. Mentions inside code spans and URLs are rewritten (they match `TASK-381`'s rule). First add `rewrite_task` raising `NotImplementedError`, then run the properties to show they fail. Write each property as a helper taking `rewrite: Callable[[Task, Mapping[TaskId, TaskId]], Task]`; the real tests pass `rewrite_task`. Also commit two wrong versions as tests that pass a wrong `rewrite` to a helper and assert it fails: (a) sequential per-key `str.replace` over each field and section `rewrite_task` touches, which turns `A` into `C` under `{A: B, B: C}`; (b) `replace_ids` over `task.render()` followed by `parse`, which changes History and `labels`.

## Acceptance Criteria

- [ ] The five `rewrite_task` properties pass; a note gives the command run (`.venv/bin/python -m unittest tests.test_property_renumbering`) and records each property failing against the `NotImplementedError` stub, with the failing test name and traceback line; the two wrong-version tests pass (each wrong version fails a property)
- [ ] `make check` passes

## History

- 2026-11-21T13:10:17Z sunny-ebony-kestrel → planning
- 2026-11-21T13:11:03Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:12:31Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:14:38Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:16:12Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:16:12Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T13:32:45Z daring-violet-puffin todo → doing
