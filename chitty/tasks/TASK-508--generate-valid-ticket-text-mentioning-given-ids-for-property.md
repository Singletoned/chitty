---
title: Generate valid ticket text mentioning given IDs, for property tests
status: planning
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-507` on 2026-11-21, after its worker found the whole ticket too large for one session. This ticket builds only the test generator; `TASK-507` uses it for the `rewrite_task` properties.

Add a Hypothesis strategy `ticket_texts(ids: list[TaskId])` to a new module `tests/ticket_strategies.py`. It draws ticket Markdown that `chitty.model.parse` accepts and that mentions IDs drawn from `ids` in every place a ticket can mention one. The `tasks` strategy in `tests/test_check_edit.py` builds tickets through the model; this one builds text, because it must reach formatting the model does not produce on its own.

What it draws:

- Frontmatter: `title` (single-line), `status` (a valid status), `created` (a date), optional `labels`, `owner`, `parent`, `depends_on` (no duplicates) and `moved_from`, each in the format `parse` accepts. The values of `title`, `labels`, `owner`, `parent`, `depends_on` and `moved_from` may mention drawn IDs.
- Sections, in `SECTION_ORDER` (`src/chitty/model.py`): `Description`, `Acceptance Criteria` (`- [ ]`, `- [x]` and `- [X]` items, some with indented continuation lines), optionally `Plan` and `Summary`, `Notes`, and `History`. Section text and criterion text mention drawn IDs, sometimes inside code spans or URLs, and sometimes as the forms `<ID>-x`, `<ID>A`, `X<ID>` and `X-<ID>`.
- Text constraints that keep the result valid: no text before the first section; no line of section text starts with `#`; no setext underline (`---` or `===` directly after a paragraph line); no line that would itself parse as a section heading or criterion where it is not meant to be one.

A draw that `parse` rejects is a bug in the strategy: never use `assume` to discard it.

Tests in a new `tests/test_ticket_strategies.py`, with `hypothesis` as the other property tests use it: every draw parses; `parse(text).render()` parses again and renders to the same text (rendering is stable); and, over many draws, each of these occurs at least once: an `[X]` criterion, a multi-line criterion, `Plan` present, `Plan` absent, an ID mention in each frontmatter field listed above, and each of the four near-miss forms. Check the "occurs at least once" part with one `@given` test that collects the draws (for example with `hypothesis.event`, or by asserting over a fixed `settings(max_examples=...)` run of a helper), not with a separate hand-picked example.

Out of scope: `rewrite_task` and its properties (`TASK-507`).

## History

- 2026-11-21T13:44:08Z sunny-ebony-kestrel → planning
