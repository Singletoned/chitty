---
title: "Add a `difficulty` field to tickets: `low`, `medium` or `high`"
status: doing
parent: TASK-308
created: 2026-11-12
---

## Description

Part of `TASK-308`. An optional `difficulty` field, so `TASK-312` can choose an agent command by it and `TASK-313` can tell planners to set it. Decided with the person, 2026-11-23: a fixed, built-in set `low`, `medium`, `high`, not configurable (unlike `priorities`). A field, not a label, because the set is closed and validated. MCP and the ticket strategy are the next ticket, which depends on this one.

Change:

- `src/chitty/model.py`: `DIFFICULTIES = ("low", "medium", "high")` next to `PRIORITIES`; `Frontmatter.difficulty: Literal["low", "medium", "high"] | None = None`; `"difficulty"` in `FIELD_ORDER` straight after `"priority"`. A hand-written value outside the set is then a frontmatter error, like any invalid frontmatter. `chitty show` and `--json` print frontmatter generically, so they need no change.
- `src/chitty/store.py`: `Edit.difficulty: str | None = None` (`""` removes), applied in `Edit.apply` and named in the History change list as `priority` is. `Repo.add` takes it through `fields`.
- `src/chitty/cli.py`: `--difficulty` on `chitty add` (`click.Choice(DIFFICULTIES)`) and on `chitty edit` (`click.Choice([*DIFFICULTIES, ""])`, help `low, medium, high; '' unsets.`). No short option. `chitty list` does not show it.
- `docs/plan/task-file.md`: a `difficulty` row after `priority` in the frontmatter table: `` `low\|medium\|high` ``, not required, `absent means unset`.

Tests in a new `tests/test_difficulty.py` (`CliTestCase` from `tests/test_cli.py`):

- `chitty add T -d x -p low --difficulty high` writes `priority: low` then `difficulty: high`; `chitty edit TASK-1 --difficulty low` writes it and the History line names `difficulty`; `--difficulty ""` removes the key.
- `--difficulty hard` on `add` and on `edit` exits 2 with Click's `'hard' is not one of` and writes nothing (no new file; the edited file byte-identical).
- `chitty show TASK-1` prints `difficulty: high`; `--json` has `"difficulty": "high"`, and `null` without one; a file written by hand with `difficulty: hard` makes `chitty check` fail with `difficulty: Input should be 'low', 'medium' or 'high'`.
- Property, Hypothesis with `examples(50)` from `tests/__init__.py`: for any text from `ticket_texts([TaskId("TASK", 1)])` (`tests/ticket_strategies.py`) and `d` in `("low", "medium", "high", "")`, `Edit(difficulty=d).apply(parse(text))` has `difficulty == (d or None)` and every other field and section unchanged.

Out of scope: MCP and `tests/ticket_strategies.py` (next ticket), `TASK-312`, `TASK-313`, `chitty list`, configurable levels.

## Acceptance Criteria

- [x] The `chitty add`, `chitty edit` (set, unset, refusal), `chitty show`, `--json` and `chitty check` cases in `tests/test_difficulty.py` pass and fail before the change
- [x] The `Edit.apply` property passes; `docs/plan/task-file.md` has the `difficulty` row; `make check` passes

## Plan

Add failing CLI and property coverage first, then implement the validated frontmatter field, edit and CLI plumbing, and document it. Format, run checks, and hand off for review.

## Notes

Before implementation, tests/test_difficulty.py failed all four tests: the CLI did not recognize the option, check rejected the unknown key, and Edit lacked the field. After implementation all four pass; make check passed.

## Summary

Added validated optional difficulty frontmatter, add/edit CLI options, history recording, documentation and property and CLI tests. MCP and strategy changes remain for the follow-up ticket.

## History

- 2026-11-12T21:44:03Z kind-yellow-vole → backlog
- 2026-11-23T19:41:24Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T19:41:24Z witty-yellow-vole backlog → planning
- 2026-11-23T19:41:37Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:43:25Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T19:43:25Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:43:36Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:44:08Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:44:10Z witty-yellow-vole planning → todo
- 2026-11-23T19:53:57Z friendly-khaki-vole todo → doing
- 2026-11-23T19:57:15Z friendly-khaki-vole: wrote the plan
- 2026-11-23T19:58:58Z friendly-khaki-vole: changed notes
- 2026-11-23T19:59:07Z friendly-khaki-vole: changed notes
- 2026-11-23T19:59:07Z friendly-khaki-vole doing → error
- 2026-11-23T23:08:22Z friendly-coral-badger: changed notes
- 2026-11-23T23:08:22Z friendly-coral-badger error → todo
- 2026-11-23T23:18:41Z plucky-khaki-wren todo → doing
- 2026-11-23T23:21:06Z plucky-khaki-wren: wrote the plan
- 2026-11-23T23:23:48Z plucky-khaki-wren: changed owner, notes
- 2026-11-23T23:23:48Z plucky-khaki-wren doing → planning
- 2026-11-26T20:08:13Z zesty-ginger-newt: changed notes
- 2026-11-26T20:08:13Z zesty-ginger-newt planning → to-plan
- 2026-11-26T20:08:16Z zesty-ginger-newt: replaced notes; changed title, description, acceptance criteria; wrote the plan
- 2026-11-26T20:08:16Z zesty-ginger-newt to-plan → planning
- 2026-11-26T20:08:18Z zesty-ginger-newt planning → cold-read
- 2026-11-26T20:09:23Z zesty-ginger-newt cold-read → planning
- 2026-11-26T20:09:28Z zesty-ginger-newt planning → todo
- 2026-11-26T20:09:55Z zesty-ginger-newt: changed title
- 2026-11-26T23:47:08Z golden-hazel-vole todo → doing
- 2026-11-26T23:50:18Z golden-hazel-vole: wrote the plan
- 2026-11-26T23:54:55Z golden-hazel-vole: changed notes, summary; ticked acceptance criteria
