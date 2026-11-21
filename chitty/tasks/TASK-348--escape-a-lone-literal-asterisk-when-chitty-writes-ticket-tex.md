---
title: Escape a lone literal asterisk when Chitty writes ticket text
status: cold-read
labels:
  - needs-minor
depends_on:
  - TASK-347
created: 2026-11-16
---

## Description

Every guide tells agents to escape a single literal `*` or wrap it in backticks. The reason is that two lone asterisks pair as emphasis in CommonMark, and prettier (3.7.4, the version `package.json` pins) then rewrites them as `_`, even inside a later code span. Checked 2026-11-17 with `prettier --parser markdown`:

- `files/*.jpg and c/*.png` becomes `files/_.jpg and c/_.png`
- ``a * b and c `*` d`` becomes ``a _ b and c `_` d``
- `a \* b and c * d` becomes `a \* b and c \* d`, which keeps its meaning

`_` is not affected, and mdformat keeps both. Have Chitty escape literal asterisks in the text it is given, so the instruction can go.

Decisions:

- Single-`*` emphasis is given up: an author who writes `*word*` gets literal asterisks. Ticket text cannot tell `files/*.jpg and c/*.png` from intended emphasis, and `_word_` and `**word**` still work. Add `needs-minor` for this.
- Add a pure function `escape_literal_asterisks(text: str) -> str` in a new module `src/chitty/markdown.py`, using `MarkdownIt("commonmark")` as `src/chitty/check.py` does. Let `shape(t)` be the CommonMark HTML of `t` with every `<em>` and `</em>` replaced by `*`. Going left to right over the text as escaped so far, it inserts `\` before a `*` exactly when `shape` of the text with that insertion equals `shape` of the caller's original input. Repeat that pass, each time comparing with `shape` of the pass's own input, until a pass changes nothing, and return that text (decided 2026-11-21: one pass is not idempotent; `**_*_` gives `**_\*_` and then `\*\*_\*_`). Every pass keeps `shape`, so the result has the original's `shape`, and a further call changes nothing. Planner probe 2026-11-21: the repeated pass gives `\*\*_\*_` for `**_*_`, and the same results as below for the other examples. So it escapes literal asterisks and single-`*` emphasis, and leaves code spans, fenced and indented code, autolinks, HTML, `**strong**` and an already escaped `\*` alone, because escaping there changes `shape`. Checked with a prototype: `files/*.jpg and c/*.png` gives `files/\*.jpg and c/\*.png`; ``x `a*b` <http://x/*>`` is unchanged; `**bold** and *em*` gives `**bold** and \*em\*`.
- Apply it to the Markdown text a caller supplies, and nowhere else: in `Edit.apply` in `src/chitty/store.py`, to `description`, the result of `replace_in_description`, `add_criteria`, the text of `set_criteria`, `plan`, `note`, `notes`, `set_notes` and `summary`; and in `new_task` in `src/chitty/model.py`, to the description and criteria (a new `-d` replaces the whole description, so all of it is escaped), which covers `chitty add` and the backlog import. `chitty suggest` (`suggest` in `src/chitty/inbox.py`) checks that the description round-trips through `new_task` and then writes its own normalized text to the suggestion file, so escaping only in `new_task` would make it refuse such descriptions. Decided 2026-11-21: in `suggest`, apply `escape_literal_asterisks` to the normalized description before building the candidate, and write that escaped text to the suggestion file; the round-trip check then compares escaped with escaped. Not to the title or other frontmatter. Do not rewrite existing files, and do not add it to `chitty fix`.
- Keep the literal-delimiter warning in `src/chitty/check.py`: hand-edited files still need it. `test_warning_does_not_fail_check` in `tests/test_cli.py` writes `static/photos/*.jpg` through `chitty add`, which will no longer warn: have it write the ticket file directly instead, keeping what it checks.
- Remove the instruction: the sentence in `src/chitty/guide.md` and the bullets in `src/chitty/roles/work.md`, `review.md` and `plan.md`. Delete `tests/test_guide_literal_star.py`, and update `tests/fixtures/guide-before-workflow.md` only if a test fails without it. Do not change `AGENTS.md` on the branch: after this lands, the main checkout's `chitty init` refreshes its managed block, and the planning session removes the same sentence from the `## Chitty` section's hand-written copy if it is outside the block.

Tests: Hypothesis properties in a new `tests/test_property_markdown_escape.py`, over text built from `*`, `_`, `\`, a backtick, `/`, `.`, `<`, `>`, `[`, `]`, `(`, `)`, `!`, `#`, `-`, a space, a tab, a newline, `1`, `a`, `b` and `é`: `shape` of the result equals `shape` of the input; escaping twice equals escaping once; and for input with no `_`, the result's CommonMark HTML contains no `<em>`. Example tests in the same file: the three prettier cases above are escaped and then formatted by the pinned prettier, as `tests/test_formatters.py` runs it, to the escaped text unchanged. A suggestion test in `tests/test_inbox.py`, in the style of `test_suggestion_is_written_to_this_test_inbox`: `chitty suggest` with description ``files/*.jpg and `x*y` `` succeeds, the suggestion file's body holds ``files/\*.jpg and `x*y` ``, and `chitty inbox --pull` creates a ticket whose Description is that escaped text. A CLI test: ``files/*.jpg and `x*y` `` given to `chitty add -d`, `chitty edit --note`, `--ac` and `--summary` is stored in the ticket file as ``files/\*.jpg and `x*y` ``.

Out of scope: `_`, titles, escaping on read and rewriting existing tickets.

## Acceptance Criteria

- [ ] Hypothesis properties in `tests/test_property_markdown_escape.py` show `escape_literal_asterisks` keeps `shape`, is idempotent, and leaves no `<em>` for input without `_`; the three prettier examples, escaped, format to themselves; the tests fail with the function raising `NotImplementedError`
- [ ] The CLI test in Tests stores ``files/\*.jpg and `x*y` `` for each of `add -d`, `edit --note`, `--ac` and `--summary`, and the suggestion test stores and imports the escaped text; both fail before the change
- [ ] No guide in `src/chitty/guide.md` or `src/chitty/roles/` tells agents to escape a literal `*`, and `tests/test_guide_literal_star.py` is gone; `make check` passes

## Notes

Cold read by a Haiku subagent, 2026-11-17. Fixed: the rule as first written (CommonMark HTML unchanged) never escaped `files/*.jpg and c/*.png`, because CommonMark itself pairs those as emphasis; it now compares HTML with `<em>` tags folded to `*`, which gives up single-`*` emphasis (decision recorded, `needs-minor`). Also fixed: which text the comparison uses, a redundant property, the generator alphabet, and the exact CLI input and stored text. Not adopted: testing every `Edit` field through the CLI; `Edit.apply` covers them in one place.

Returned to planning: two requirements conflict with the code or each other, and need decisions before implementation.

1. The specified one-pass, left-to-right shape comparison is not idempotent, contrary to criterion 1. Using CommonMark and the specified algorithm, `**_*_` becomes `**_\*_` on the first pass and `\*\*_\*_` on the second. The first two insertions change the original shape when first visited, but become shape-preserving after the later insertion; folding underscore emphasis into `*` causes this. Decide whether to change the algorithm or the idempotence requirement, and specify expected behavior for this case.

2. The claim that changing `new_task` covers `chitty suggest` is wrong: `src/chitty/inbox.py:suggest` compares the candidate description with the unescaped normalized input and raises if they differ, then writes the original description directly to the suggestion file. Escaping in `new_task` alone therefore rejects descriptions needing escaping rather than storing escaped suggestions. Decide how suggestion validation and storage should change, and specify a regression test including fixture, action and assertions for that path.

No implementation changes were made; the prototype was run in memory against the checkout environment. Full checks and regression verification remain unfinished.

Replanned 2026-11-21: both blockers above settled in the Description (repeat the pass to a fixed point; `suggest` escapes before validating and stores the escaped text).

## History

- 2026-11-16T09:59:59Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:42Z intrepid-coral-raven backlog → planning
- 2026-11-17T19:57:03Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T19:57:06Z kind-umber-toad: changed owner
- 2026-11-17T19:57:06Z kind-umber-toad planning → cold-read
- 2026-11-17T19:58:42Z kind-umber-toad: changed labels, description, acceptance criteria, notes
- 2026-11-17T19:58:42Z kind-umber-toad cold-read → planning
- 2026-11-17T20:01:19Z kind-umber-toad: changed dependencies
- 2026-11-17T20:22:21Z kind-umber-toad: changed owner
- 2026-11-17T20:22:21Z kind-umber-toad planning → todo
- 2026-11-20T22:13:39Z nimble-ginger-kestrel todo → doing
- 2026-11-20T22:15:39Z nimble-ginger-kestrel: changed owner, notes
- 2026-11-20T22:15:39Z nimble-ginger-kestrel doing → planning
- 2026-11-21T23:20:33Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-21T23:20:33Z lively-zinc-newt planning → cold-read
