---
title: Escape lone literal asterisks in Markdown text with a pure function
status: doing
depends_on:
  - TASK-347
created: 2026-11-16
---

## Description

Every guide tells agents to escape a single literal `*` or wrap it in backticks, because two lone asterisks pair as emphasis in CommonMark, and prettier (3.7.4, pinned in `package.json`) then rewrites them as `_`, even inside a later code span. Checked 2026-11-17 with `prettier --parser markdown`:

- `files/*.jpg and c/*.png` becomes `files/_.jpg and c/_.png`
- ``a * b and c `*` d`` becomes ``a _ b and c `_` d``
- `a \* b and c * d` becomes `a \* b and c \* d`, which keeps its meaning

This ticket adds the pure escaping function only (split 2026-11-21; wiring is `TASK-529`, `chitty suggest` is `TASK-530`, removing the guide instruction is `TASK-531`). Nothing calls it yet.

Add `escape_literal_asterisks(text: str) -> str` in a new module `src/chitty/markdown.py`, using `MarkdownIt("commonmark")` as `src/chitty/check.py` does. Let `shape(t)` be the CommonMark HTML of `t` with every `<em>` and `</em>` replaced by `*`. One pass goes left to right over every `*` in the text, including one already preceded by `\`, and inserts `\` before it exactly when `shape` of the text with that insertion (and the insertions made so far) equals `shape` of the pass's input. Repeat passes until one changes nothing, and return that text. Every pass keeps `shape`, so the result has the input's `shape` and a further call changes nothing; passes are bounded by the number of `*`. One pass alone is not idempotent: `**_*_` gives `**_\*_`, then `\*\*_\*_`.

So it escapes literal asterisks and single-`*` emphasis (single-`*` emphasis is given up; `_word_` and `**word**` still work), and leaves code spans, fenced and indented code, autolinks, HTML, `**strong**` and an already escaped `\*` alone, because escaping there changes `shape`. Planner probes 2026-11-21: `files/*.jpg and c/*.png` gives `files/\*.jpg and c/\*.png`; ``x `a*b` <http://x/*>`` is unchanged; `**bold** and *em*` gives `**bold** and \*em\*`; `**_*_` gives `\*\*_\*_`; `a\*b` is unchanged. A cold reader's fuzz of 3000 strings found at most two passes, no change of `shape` and no non-idempotent result.

Tests: Hypothesis properties in a new `tests/test_property_markdown_escape.py`, over text built from `*`, `_`, `\`, a backtick, `/`, `.`, `<`, `>`, `[`, `]`, `(`, `)`, `!`, `#`, `-`, a space, a tab, a newline, `1`, `a`, `b` and `é`: `shape` of the result equals `shape` of the input; escaping twice equals escaping once; and for input with no `_`, the result's CommonMark HTML contains no `<em>`. Example tests in the same file: each probe example above gives the stated result, and the three prettier cases above, escaped, are formatted by the pinned prettier (through the `run_formatter` helper in `tests/test_formatters.py`, imported from there) to the escaped text unchanged. Before implementing, add the function raising `NotImplementedError` and confirm the tests fail.

## Acceptance Criteria

- [ ] The Hypothesis properties in `tests/test_property_markdown_escape.py` show `escape_literal_asterisks` keeps `shape`, is idempotent, and leaves no `<em>` for input without `_`; the probe examples give their stated results; the three prettier examples, escaped, format to themselves; the tests fail with the function raising `NotImplementedError`
- [ ] `make check` passes

## Plan

Add property and formatter regression tests against a stub, verify failure, then implement fixed-point CommonMark shape comparison and run project checks.

## Notes

Cold read by a Haiku subagent, 2026-11-17. Fixed: the rule as first written (CommonMark HTML unchanged) never escaped `files/*.jpg and c/*.png`, because CommonMark itself pairs those as emphasis; it now compares HTML with `<em>` tags folded to `*`, which gives up single-`*` emphasis (decision recorded, `needs-minor`). Also fixed: which text the comparison uses, a redundant property, the generator alphabet, and the exact CLI input and stored text. Not adopted: testing every `Edit` field through the CLI; `Edit.apply` covers them in one place.

Returned to planning: two requirements conflict with the code or each other, and need decisions before implementation.

1. The specified one-pass, left-to-right shape comparison is not idempotent, contrary to criterion 1. Using CommonMark and the specified algorithm, `**_*_` becomes `**_\*_` on the first pass and `\*\*_\*_` on the second. The first two insertions change the original shape when first visited, but become shape-preserving after the later insertion; folding underscore emphasis into `*` causes this. Decide whether to change the algorithm or the idempotence requirement, and specify expected behavior for this case.

2. The claim that changing `new_task` covers `chitty suggest` is wrong: `src/chitty/inbox.py:suggest` compares the candidate description with the unescaped normalized input and raises if they differ, then writes the original description directly to the suggestion file. Escaping in `new_task` alone therefore rejects descriptions needing escaping rather than storing escaped suggestions. Decide how suggestion validation and storage should change, and specify a regression test including fixture, action and assertions for that path.

No implementation changes were made; the prototype was run in memory against the checkout environment. Full checks and regression verification remain unfinished.

Replanned 2026-11-21: both blockers above settled in the Description (repeat the pass to a fixed point; `suggest` escapes before validating and stores the escaped text).

The new regression suite failed against the NotImplementedError stub as required.

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
- 2026-11-21T23:21:57Z lively-zinc-newt: changed title, labels, description, acceptance criteria
- 2026-11-21T23:23:33Z lively-zinc-newt: changed description
- 2026-11-21T23:23:33Z lively-zinc-newt cold-read → todo
- 2026-11-21T23:27:03Z brisk-indigo-eel todo → doing
- 2026-11-21T23:28:45Z brisk-indigo-eel: wrote the plan
- 2026-11-21T23:29:04Z brisk-indigo-eel: changed notes
