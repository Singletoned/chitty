---
title: Escape lone literal asterisks in text given to `chitty add` and `chitty edit`
status: cold-read
labels:
  - needs-minor
depends_on:
  - TASK-348
parent: TASK-348
created: 2026-11-21
---

## Description

Split from `TASK-348` on 2026-11-21. `TASK-348` adds `escape_literal_asterisks` in `src/chitty/markdown.py`. This ticket applies it to the Markdown text a caller supplies, so Chitty stores lone literal asterisks escaped and prettier cannot turn them into emphasis. `TASK-348` landed `escape_literal_asterisks(text: str) -> str` (rechecked on `main` 2026-11-21). Escaping applies to the whole resulting section, so a `replace_in_description` or `set_notes` edit also escapes lone asterisks already in that section; that is accepted. Runner notes go through `Edit.note` too; their fenced output is left alone because escaping inside code changes `shape`.

- Apply it in `Edit.apply` in `src/chitty/store.py` to `description`, the result of `replace_in_description`, `add_criteria`, the text of `set_criteria`, `plan`, `note`, `notes`, `set_notes` and `summary`; and in `new_task` in `src/chitty/model.py` to the description and criteria (covers `chitty add` and `src/chitty/import_backlog.py`). Not to the title or other frontmatter. Do not rewrite existing files, and do not add it to `chitty fix`. `chitty suggest` is `TASK-530`.
- Single-`*` emphasis is given up (`needs-minor`): an author who writes `*word*` gets literal asterisks.
- Keep the literal-delimiter warning in `src/chitty/check.py`: hand-edited files still need it. `test_warning_does_not_fail_check` in `tests/test_cli.py` writes `static/photos/*.jpg` through `chitty add`, which will no longer warn: have it write the ticket file directly instead, keeping what it checks.

Test: ``files/*.jpg and `x*y` `` given to `chitty add -d`, `chitty edit --note`, `--ac` and `--summary` is stored in the ticket file as ``files/\*.jpg and `x*y` ``.

## Acceptance Criteria

- [ ] The CLI test stores ``files/\*.jpg and `x*y` `` for each of `add -d`, `edit --note`, `--ac` and `--summary`, and fails before the change
- [ ] `test_warning_does_not_fail_check` writes its file directly and keeps its assertions; `make check` passes

## History

- 2026-11-21T23:22:17Z lively-zinc-newt → planning
- 2026-11-21T23:40:10Z lively-zinc-newt: changed description
- 2026-11-21T23:40:10Z lively-zinc-newt planning → cold-read
