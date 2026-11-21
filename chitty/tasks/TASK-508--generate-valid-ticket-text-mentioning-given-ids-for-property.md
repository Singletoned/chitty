---
title: Generate valid ticket text mentioning given IDs, for property tests
status: cold-read
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-507` on 2026-11-21, after its worker found the whole ticket too large for one session. This ticket builds only the test generator; `TASK-507` uses it for the `rewrite_task` properties.

Add a Hypothesis strategy `ticket_texts(ids: list[TaskId])` to a new module `tests/ticket_strategies.py`. `ids` is non-empty. It draws ticket Markdown that `chitty.model.parse` accepts and that mentions IDs drawn from `ids` wherever a ticket can mention one. (The `tasks` strategy in `tests/test_check_edit.py` builds tickets through the model; this one builds text, because it must reach formatting the model does not produce itself, such as `[X]` and continuation lines.)

Rules from `src/chitty/model.py` the text must follow; check each against the source:

- The text uses `\n` line endings only (no `\r`) and ends with `\n`.
- Frontmatter: `title` (single-line), `status` (a valid status), `created` (a `YYYY-MM-DD` date), and optionally `priority` (`low`, `medium` or `high`), `labels` and `depends_on` (YAML lists; `depends_on` without duplicates), `owner`, `parent` and `moved_from` (strings), and `provisional: true`. `title`, `labels`, `owner`, `parent`, `depends_on` and `moved_from` may mention drawn IDs.
- Sections in `SECTION_ORDER`: a non-empty `Description`; `Acceptance Criteria` (items `- [ ]`, `- [x]` or `- [X]`, some followed by an indented continuation line); optional `Plan` and `Summary`; `Notes`; and `History` last, non-empty, each line matching `HISTORY_LINE_RE` or `HISTORY_EVENT_RE` (an event's action text may mention IDs).
- No text before the first section. Outside fenced code, no line of section text matches `HEADING_RE` or (outside Acceptance Criteria) `CRITERION_RE`, and no line matching `SETEXT_UNDERLINE_RE` follows a paragraph line. Fenced code is not needed; leave it out.
- Section and criterion text mentions drawn IDs, sometimes inside code spans or URLs, and sometimes in the forms `<ID>-x`, `<ID>A`, `X<ID>` and `X-<ID>`.

A draw that `parse` rejects is a bug in the strategy: never use `assume` to discard it. The drawn text need not be canonical; what matters is that `parse` accepts it and that rendering is stable.

Tests in a new `tests/test_ticket_strategies.py`, passing a fixed list such as `[TaskId.parse("TASK-1"), TaskId.parse("TASK-22")]`:

- A `@given` test: every draw parses, and `parse(text).render()` parses again and renders to the same text (`parse(r).render() == r` for `r = parse(text).render()`).
- One test method per feature, using `hypothesis.find(ticket_texts(ids), predicate)`, which raises if nothing matches. Predicates check parsed values where they can: a `[X]` criterion (raw text has a line starting `- [X]`); a criterion followed by an indented continuation line; `Plan` present; `Plan` absent; for each of `title`, `labels`, `owner`, `parent`, `depends_on` and `moved_from`, a drawn ID in that parsed frontmatter value; and each near-miss form, checked as an exact string (for example `"TASK-1A" in text` and `"TASK-12" not in text` for the `<ID>A` case, so a longer ID does not count).

Out of scope: `rewrite_task` and its properties (`TASK-507`).

## Acceptance Criteria

- [ ] Every draw of `ticket_texts` parses, and `parse(text).render()` re-parses and renders to the same text (a `@given` test in `tests/test_ticket_strategies.py`)
- [ ] `hypothesis.find` finds an example of each listed feature (one test method per feature): an `[X]` criterion, a multi-line criterion, `Plan` present and absent, an ID mention in each listed frontmatter field, and each near-miss form
- [ ] `make check` passes

## History

- 2026-11-21T13:44:08Z sunny-ebony-kestrel → planning
- 2026-11-21T13:44:19Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T13:44:19Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:45:51Z sunny-ebony-kestrel: changed description
