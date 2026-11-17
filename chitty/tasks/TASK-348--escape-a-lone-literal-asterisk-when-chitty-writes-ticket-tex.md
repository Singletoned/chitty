---
title: Escape a lone literal asterisk when Chitty writes ticket text
status: cold-read
owner: planner-cold-read
created: 2026-11-16
---

## Description

Every guide tells agents to escape a single literal `*` or wrap it in backticks. The reason is prettier (3.7.4, the version `package.json` pins): it pairs two literal asterisks that CommonMark leaves alone and rewrites them as `_` emphasis, even inside a later code span. Checked 2026-11-17 with `prettier --parser markdown`:

- `files/*.jpg and c/*.png` becomes `files/_.jpg and c/_.png`
- ``a * b and c `*` d`` becomes ``a _ b and c `_` d``
- `a \* b and c * d` becomes `a \* b and c \* d`, which keeps its meaning

`_` is not affected, and mdformat keeps both. Have Chitty escape literal asterisks in the text it is given, so the instruction can go.

Decisions:

- Add a pure function `escape_literal_asterisks(text: str) -> str` in a new module `src/chitty/markdown.py`, using `MarkdownIt("commonmark")` as `src/chitty/check.py` does. Going left to right, it inserts `\` before each `*` exactly when the CommonMark HTML of the text with that one insertion (applied to the text as escaped so far) equals the HTML of the original text. That leaves code spans, fenced and indented code, autolinks, link destinations, HTML and real emphasis alone, because escaping there changes the HTML, and it leaves an already escaped `\*` alone, for the same reason.
- Apply it to the Markdown text a caller supplies, and nowhere else: in `Edit.apply` in `src/chitty/store.py`, to `description`, the result of `replace_in_description`, `add_criteria`, the text of `set_criteria`, `plan`, `note`, `notes`, `set_notes` and `summary`; and in `new_task` in `src/chitty/model.py`, to the description and criteria, which covers `chitty add`, `chitty suggest` (through `src/chitty/inbox.py`) and the backlog import. Not to the title or other frontmatter. Do not rewrite existing files, and do not add it to `chitty fix`.
- Keep the literal-delimiter warning in `src/chitty/check.py`: hand-edited files still need it. `test_warning_does_not_fail_check` in `tests/test_cli.py` writes `static/photos/*.jpg` through `chitty add`, which will no longer warn: have it write the ticket file directly instead, keeping what it checks.
- Remove the instruction: the sentence in `src/chitty/guide.md` and the bullets in `src/chitty/roles/work.md`, `review.md` and `plan.md`. Delete `tests/test_guide_literal_star.py`, and update `tests/fixtures/guide-before-workflow.md` only if a test fails without it. Do not change `AGENTS.md` on the branch: after this lands, the main checkout's `chitty init` refreshes its managed block, and the planning session removes the same sentence from the `## Chitty` section's hand-written copy if it is outside the block.

Tests: Hypothesis properties in a new `tests/test_property_markdown_escape.py`, over text built from `*`, `_`, `\`, a backtick, `/`, `.`, a space, a newline and two letters: escaping keeps the CommonMark HTML unchanged; escaping twice equals escaping once; and the result contains no `*` that the function would still escape. Example tests in the same file for the three prettier cases above, run through the pinned prettier as `tests/test_formatters.py` does, showing the escaped text formats to itself. A CLI test that `chitty add` and `chitty edit --note` with `files/*.jpg` store `files/\*.jpg`.

Out of scope: `_`, titles, escaping on read and rewriting existing tickets.

## Acceptance Criteria

- [ ] Hypothesis properties in `tests/test_property_markdown_escape.py` show `escape_literal_asterisks` keeps the CommonMark HTML, is idempotent and leaves no escapable `*`; the three prettier examples format to themselves once escaped; the tests fail with the function raising `NotImplementedError`
- [ ] `chitty add -d` and `chitty edit --note`, `--ac` and `--summary` store `files/*.jpg` as `files/\*.jpg`, and a code span containing `*` is stored unchanged; the test fails before the change
- [ ] No guide in `src/chitty/guide.md` or `src/chitty/roles/` tells agents to escape a literal `*`; `make check` passes

## History

- 2026-11-16T09:59:59Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:42Z intrepid-coral-raven backlog → planning
- 2026-11-17T19:57:03Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T19:57:06Z kind-umber-toad: changed owner
- 2026-11-17T19:57:06Z kind-umber-toad planning → cold-read
