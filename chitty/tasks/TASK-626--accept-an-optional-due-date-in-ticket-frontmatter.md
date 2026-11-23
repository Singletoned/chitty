---
title: Accept an optional `due` date in ticket frontmatter
status: cold-read
parent: TASK-619
created: 2026-11-23
---

## Description

Part of TASK-619 (optional due dates, requested by the person on 2026-11-23). This ticket covers only the file format; setting `due` from the CLI is TASK-628, and showing it is TASK-627.

Change, in `src/chitty/model.py`:

- `Frontmatter` gets `due: date | None = None`, declared after `created`.
- Add `"due"` to `FIELD_ORDER` straight after `"created"`, so `with_field("due", ...)` inserts the line after `created:`.
- Extend the `created` before-validator (`_created`, `@field_validator("created", mode="before")`) to cover `due` as well, so a string that is not `YYYY-MM-DD` raises `'<value>' is not an ISO 8601 date (YYYY-MM-DD)`. A well-formed but impossible date such as `2026-13-01` gets pydantic's message, as `created` does today.
- `_render_field` already writes a `date` value unquoted (`due: 2026-12-01`); nothing to change there.

Because `as_dict` uses `model_dump(mode="json")`, `chitty show --json` and `chitty list --json` gain a `due` key: an ISO string, or `null` when there is no due date. Update any existing test that compares a whole dict or JSON object, and say which ones in a note.

`chitty check` already reports frontmatter errors as `<absolute path>: <field>: <message>`. For example, a bad `created` gives `.../TASK-1--t.md: created: '23-11-2026' is not an ISO 8601 date (YYYY-MM-DD)`. `due` gets this for free.

Tests, in a new `tests/test_due_date.py`:

- Parse and render: a ticket text with `due: 2026-12-01` after `created:` parses with `frontmatter.due == date(2026, 12, 1)`, and `render()` returns the text byte for byte. A ticket without `due` has `frontmatter.due is None`.
- `parse(text).with_field("due", date(2026, 12, 1)).render()` has the line `due: 2026-12-01\n` directly after the `created:` line, and `with_field("due", None)` removes it again, giving the original text.
- Malformed: with `due: 01-12-2026`, `parse` raises `TaskError` whose message is `due: '01-12-2026' is not an ISO 8601 date (YYYY-MM-DD)`. With `due: 2026-13-01`, the message starts with `due: `.
- `chitty check`: in a `RepoTestCase` repository, write a ticket file with `due: 01-12-2026` into `chitty/tasks/`. Run `chitty check` through `click.testing.CliRunner` with `chitty.cli.cli`. It exits non-zero, and the output contains `<the file's absolute path>: due: '01-12-2026' is not an ISO 8601 date (YYYY-MM-DD)`.
- JSON: `as_dict()["due"]` is `"2026-12-01"` for the first ticket and `None` for a ticket without `due`.
- Formatters: in `tests/test_formatters.py`, add `"due": date(2026, 11, 30)` to `sample()`'s `fields`, so the prettier and mdformat no-op tests cover it.

Out of scope: CLI options, MCP, `chitty list` display, filtering and sorting.

## Acceptance Criteria

- [ ] The parse, render, `with_field`, malformed, `chitty check` and JSON tests in `tests/test_due_date.py` pass and fail before the change. Record both runs in a note
- [ ] The prettier and mdformat tests in `tests/test_formatters.py` pass with `due` in `sample()`; `make check` passes

## History

- 2026-11-23T10:39:46Z witty-russet-gannet → backlog
- 2026-11-23T12:27:20Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T12:27:20Z witty-russet-gannet backlog → cold-read
