---
title: Rewrite provisional ID mentions in a parsed ticket (`rewrite_task`)
status: doing
depends_on:
  - TASK-508
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-391` on 2026-11-21: the pure rewrite and its property are separable from the store method, which then calls this. `plan_renumbering` and `replace_ids` (`TASK-381`) are in `src/chitty/renumbering.py`.

Decisions:

- New pure function `rewrite_task(task: Task, mapping: Mapping[TaskId, TaskId]) -> Task` in `src/chitty/renumbering.py`: `replace_ids` on `title`, `depends_on`, `parent`, and every section except `History`, which is append-only (a ticket has no text before its first section: `_split_sections` in `src/chitty/model.py` rejects it); no other frontmatter field is rewritten (`labels`, `owner`, `priority`, `status`, `created`, `provisional`, `moved_from`); Acceptance Criteria per item in two calls, because a `set_criteria` item comes back unchecked and `with_section` refuses that section: `with_criteria(add=(), remove=(), set_criteria=<changed items>, check=(), uncheck=())`, then `with_criteria(add=(), remove=(), set_criteria=(), check=<indices of the changed items that were checked before>, uncheck=())`. (Clearing `provisional` on a renumbered ticket is `TASK-391`'s job, not this function's.) `moved_from` is not rewritten, so a renumbered file's own `moved_from` and History keep the provisional ID.
- Contract (decided 2026-11-21): every target in `mapping` is an ID the ticket does not mention, since `plan_renumbering` allocates fresh numbers. So rewriting `depends_on` cannot create duplicates. `rewrite_task` need not check this; callers guarantee it. Chains such as `{A: B, B: C}` still satisfy the contract when only `A` is mentioned (`B` and `C` are unmentioned targets); `A` must become `B`, and a sequential replace that then turns that `B` into `C` is wrong.
- Acceptance Criteria: call `with_criteria` only when at least one item's text changes, and then re-set only the changed items. `with_criteria` writes a re-set item as one `- [ ]` line (continuation lines folded into it); the second call then checks again the changed items that were checked before, written `[x]`. For a changed item, that folding and the lower-case `[x]` are accepted. Unchanged items keep their exact formatting, including `[X]` and continuation lines.
- Set `title`, `parent` and `depends_on` with `Task.with_field` (`src/chitty/model.py`). Never run `replace_ids` over rendered text, which would also touch `labels`, `owner` and History.
- Call `with_section` only for a section whose `replace_ids` output differs from its current text; `with_section` normalises blank lines, so an untouched section must not be re-set. With an empty mapping nothing is re-set.
- Mentions follow `replace_ids` exactly (`TASK-381`): an ID followed by `-` (`TASK-1-foo`) is a mention and is rewritten; an ID preceded by a letter, digit or `-` (`XTASK-1`, `X-TASK-1`) or followed by a letter or digit (`TASK-1A`) is not.
- Out of scope: files, Git and `Repo` (that is `TASK-391`).

Tests: Hypothesis properties in `tests/test_property_renumbering.py` (`TASK-381`'s file). Draw ticket text with `ticket_texts(ids)` from `tests/ticket_strategies.py` (`TASK-508`, which lands first and guarantees valid, varied tickets), and `parse` it to get the input `task`; compare outputs with `render()`. Draw targets with numbers above every number in `ids`, and `assume(str(target) not in text)` for each (this ticket's own `assume`; `TASK-508`'s strategy does not use one). Generate an injective mapping whose targets appear nowhere in the generated ticket (distinct keys map to distinct, fresh targets, as `plan_renumbering` guarantees) that covers some of those IDs but not others, and sometimes chains (`{A: B, B: C}`, where the chain keys after the first, here `B`, are not mentioned in the ticket, so only `A` is). Properties: (1) on `frontmatter`: `rewritten.frontmatter.title == replace_ids(task.frontmatter.title, mapping)`, `rewritten.frontmatter.parent` is `replace_ids` of the old `parent` (or `None`), and `rewritten.frontmatter.depends_on == [replace_ids(d, mapping) for d in task.frontmatter.depends_on]` position by position; and for every section other than History and Acceptance Criteria `rewritten.section(name) == strip_trailing(replace_ids(task.section(name), mapping))` for each section the mapping changes, where `strip_trailing` removes trailing spaces and tabs from every line, as `with_section` does (decided 2026-11-21: that normalisation of a changed section is accepted; an unchanged section is covered byte-for-byte by property (6)) (parsed text, not bytes; an absent section stays absent, a `None` `parent` stays `None`, and an empty `depends_on` stays empty); `len(rewritten.criteria) == len(task.criteria)`, and for each criterion `i`, `rewritten.criteria[i].text == replace_ids(task.criteria[i].text, mapping)` and `checked` is unchanged; so each mention becomes its image in one pass (with `{A: B, B: C}`, `A` becomes `B`, never `C`); (2) an unmapped ID stays unchanged, and the near misses `<KEY>A`, `X<KEY>` and `X-<KEY>` built from a mapped key stay unchanged, while `<KEY>-x` is rewritten; (3) the rendered `History` section, `labels`, `owner`, `moved_from` and every other frontmatter field are byte-identical; (4) each criterion keeps its checked state; (5) with an empty mapping, `rewrite_task(task, {}).render() == task.render()` (a regression guard); (6) with a mapping that changes some sections and criteria but not others, each section whose text `replace_ids` leaves unchanged renders byte-identically (its lines from its heading up to the next heading), and so does each criterion whose text is unchanged, including `[X]` and continuation lines. Mentions inside code spans and URLs are rewritten (they match `TASK-381`'s rule). First add `rewrite_task` raising `NotImplementedError`, then run the properties to show they fail. Write each property as a helper taking `rewrite: Callable[[Task, Mapping[TaskId, TaskId]], Task]`; the real tests pass `rewrite_task`. Also commit two wrong versions as tests that pass a wrong `rewrite` to a helper and assert the helper raises `AssertionError` (not any exception): (a) sequential per-key `str.replace` over each field and section `rewrite_task` touches, iterating the mapping in insertion order (the chain fixture is built as `{A: B, B: C}` in that order), which turns `A` into `C` under `{A: B, B: C}`; (b) `replace_ids` over `task.render()` followed by `parse`, which changes History and `labels`.

## Acceptance Criteria

- [ ] The six `rewrite_task` properties pass; a note gives the command run (`.venv/bin/python -m unittest tests.test_property_renumbering`) and records each property failing against the `NotImplementedError` stub, with the failing test name and traceback line; the two wrong-version tests pass (each wrong version fails a property)
- [ ] `make check` passes

## Plan

Generate property cases and mutation checks, confirm each property fails against a stub, then implement selective immutable rewriting and run the full checks.

## Notes

Earlier notes (the worker's two contract questions and the split) are in Git history; the Description is authoritative. Both questions are settled there: fresh targets, and criteria compared by parsed text and checked state. The generator is `TASK-508`. Decided 2026-11-21: properties (2), (3), (4) and (6) state exact expected values, so they need no wrong-version tests beyond (a) and (b).

Stub regression: `.venv/bin/python -m unittest tests.test_property_renumbering` failed for `test_boundaries`, `test_checks`, `test_empty`, `test_fields`, `test_formatting`, and `test_preserved`, each with `NotImplementedError` at `src/chitty/renumbering.py:35` in `rewrite_task`.

Returned to planning: the requirement that every changed section equals `replace_ids` of its original parsed text conflicts with the prescribed `with_section` implementation. `tests/ticket_strategies.py` generates trailing spaces; for Description `Text  TASK-1 `, mapping `TASK-1` to `TASK-100` requires `Text  TASK-100 `, but `Task.with_section` calls `_text_lines`, which strips trailing whitespace from every line, producing `Text  TASK-100`. The generated `test_fields` fails on this case. Decide whether changed sections must preserve trailing whitespace (and how to implement that without changing the prescribed API), or whether the contract should explicitly permit this normalization and update its property. The partial implementation and six initial property helpers are committed; the two required wrong-version tests and full property coverage remain unfinished. `make check` passed formatting, lint and pyright but failed `test_fields`; verification is incomplete.

The preceding note describes a conflict between exact section text preservation and the prescribed section-editing API; a planning decision is needed before implementation can proceed.

Planner 2026-11-21: accepted `with_section`'s trailing-whitespace stripping for changed sections. Property (1) compares against `replace_ids` output with trailing spaces and tabs removed from each line; unchanged sections stay byte-identical (property 6).

## History

- 2026-11-21T13:10:17Z sunny-ebony-kestrel → planning
- 2026-11-21T13:11:03Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:12:31Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:14:38Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:16:12Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:16:12Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T13:32:45Z daring-violet-puffin todo → doing
- 2026-11-21T13:35:46Z daring-violet-puffin: changed owner, notes
- 2026-11-21T13:35:46Z daring-violet-puffin doing → planning
- 2026-11-21T13:37:15Z sunny-ebony-kestrel: changed description, notes
- 2026-11-21T13:37:15Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:38:40Z sunny-ebony-kestrel: changed description
- 2026-11-21T13:39:52Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:39:52Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T13:40:09Z vivid-ochre-badger todo → doing
- 2026-11-21T13:42:17Z vivid-ochre-badger: wrote the plan
- 2026-11-21T13:42:42Z vivid-ochre-badger: changed owner, notes
- 2026-11-21T13:42:42Z vivid-ochre-badger doing → planning
- 2026-11-21T13:44:31Z sunny-ebony-kestrel: changed dependencies, description, notes
- 2026-11-21T13:47:11Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:49:09Z sunny-ebony-kestrel: replaced notes; changed description
- 2026-11-21T13:49:09Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T13:49:24Z sunny-ebony-kestrel: changed description
- 2026-11-21T13:59:37Z youthful-coral-heron todo → doing
- 2026-11-21T14:01:22Z youthful-coral-heron: wrote the plan
- 2026-11-21T14:02:12Z youthful-coral-heron: changed notes
- 2026-11-21T14:04:40Z youthful-coral-heron: changed notes
- 2026-11-21T14:04:45Z youthful-coral-heron: changed owner, notes
- 2026-11-21T14:04:45Z youthful-coral-heron doing → planning
- 2026-11-21T14:06:24Z sunny-ebony-kestrel: changed description, notes
- 2026-11-21T14:06:24Z sunny-ebony-kestrel planning → todo
- 2026-11-21T14:07:00Z quick-lilac-heron todo → doing
