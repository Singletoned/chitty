---
title: Plan provisional renumbering and rewrite ID mentions in pure functions
status: planning
depends_on:
  - TASK-380
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` (`TASK-380`, `TASK-389`), and `chitty renumber` with no path later gives it a sequential number on `main` and rewrites mentions of it (`TASK-391`). This ticket builds only the pure core that command uses, with no caller.

Decisions:

- New module `src/chitty/renumbering.py`. Create it first with these names raising `NotImplementedError`, so the tests fail on behaviour rather than at import.
- `plan_renumbering(used: Mapping[str, set[int]], provisional: Sequence[TaskId]) -> dict[TaskId, TaskId]`. `used` maps each prefix to the sequential numbers already taken in its context (prefixes are unique across contexts: `src/chitty/config.py` rejects duplicates). Each prefix's provisional IDs, in sorted `TaskId` order, get the consecutive numbers starting one above the highest used number of that prefix (from 1 when none). A provisional ID listed twice raises `ChittyError` naming it: two branches can draw the same suffix. A non-provisional ID (an `int` number) in `provisional` also raises `ChittyError`.
- `replace_ids(text: str, mapping: Mapping[TaskId, TaskId]) -> str` replaces every mention of each old ID. A mention is the old ID matched by the ASCII regular expression `(?<![A-Za-z0-9-])<ID>(?![A-Za-z0-9])`, case-sensitive. So mentions after a backtick, `(`, `[`, `"`, `/`, `_` or at line start are rewritten, and so are `TASK-K7Q2MX--slug.md` and `TASK-K7Q2MX-foo`; `XTASK-K7Q2MX`, `-TASK-K7Q2MX`, `TASK-K7Q2MXY` and lower-case forms such as the branch name `task-k7q2mx` are not. Accepted: a lower-case mention then dangles.
- Which parts of which files `replace_ids` is applied to is `TASK-391`'s decision.

Tests: Hypothesis properties in a new `tests/test_property_renumbering.py`. Generate prefixes matching `[A-Z]+`, sets of used numbers, provisional IDs from `ids.provisional_suffix` (`TASK-380`) with random draws (deduplicated, except in the duplicate test), and text mixing bounded mentions, look-alikes (each form listed above), lower-case forms and unrelated text. The `replace_ids` oracle is built independently in the test (for example, by inserting known mentions at known places in generated text), not by calling the same regular expression.

## History

- 2026-11-18T16:20:09Z lively-quartz-crane → backlog
- 2026-11-18T16:23:20Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:28:42Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:30:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:30:08Z lively-quartz-crane backlog → planning
- 2026-11-18T16:30:16Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:30:29Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:34:46Z lively-quartz-crane: changed title, dependencies, description, acceptance criteria
- 2026-11-18T16:34:46Z lively-quartz-crane cold-read → planning
