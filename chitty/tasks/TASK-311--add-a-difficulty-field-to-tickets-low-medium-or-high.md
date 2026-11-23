---
title: "Add a `difficulty` field to tickets: `low`, `medium` or `high`"
status: doing
parent: TASK-308
created: 2026-11-12
---

## Description

Part of TASK-308. An optional `difficulty` field, so that `TASK-312` can choose an agent command by it and `TASK-313` can tell planners to set it. Decided with the person, 2026-11-23: a fixed, built-in set `low`, `medium`, `high`, not configurable (unlike priorities in `TASK-632`); configurable levels can come later if `TASK-312` needs them.

A field rather than a label: the set is closed and validated. It follows how `priority` works on `main` today, field by field:

- Model (`src/chitty/model.py`): `DIFFICULTIES = ("low", "medium", "high")`, next to `PRIORITIES`. `Frontmatter.difficulty: Literal["low", "medium", "high"] | None = None`, and `"difficulty"` in `FIELD_ORDER` straight after `"priority"`. A hand-written value outside the set is then a frontmatter error, reported by `chitty check` and refused by other commands, as for any invalid frontmatter. `chitty show` and every `--json` and MCP output already print frontmatter fields generically (`_format` in `src/chitty/cli.py` walks `FIELD_ORDER`; `Task.as_dict` dumps the frontmatter), so they show it with no further change.
- Store (`src/chitty/store.py`): `Edit.difficulty: str | None = None` (`""` removes), applied in `Edit.apply` as `priority` is (`with_field("difficulty", self.difficulty or None)`), and named `difficulty` in the History change list, as `priority` is. `Repo.add` takes it through `fields` like `priority`.
- CLI (`src/chitty/cli.py`): `chitty add --difficulty` with `type=click.Choice(DIFFICULTIES)`, and `chitty edit --difficulty` with help `low, medium, high; '' unsets.` and a callback that accepts `DIFFICULTIES` or `""`, as `_priority` does for `-p`. No short option.
- MCP (`src/chitty/mcp.py`): `Difficulty = Literal["low", "medium", "high"]`; the add tool takes `difficulty: Difficulty | None = None` and the edit tool `difficulty: Difficulty | Literal[""] | None = None`, passed through as `priority` is. Add `difficulty` to the edit tool's `'' unsets priority/owner/plan` description.
- `chitty list` does not show difficulty (decided while planning: the list has no spare column, and `TASK-312` uses the field without displaying it).
- Docs: a `difficulty` row in the frontmatter table of `docs/plan/task-file.md`, after `priority`: `` `low\|medium\|high` ``, not required, `absent means unset`.

`TASK-632` (in `todo`) changes the `priority` code in the same places (`-p` loses its `click.Choice`, `Priority` becomes `str`); this ticket does not depend on it and must not change `priority`. If `TASK-632` has landed first, keep `difficulty` as specified here anyway: it stays a fixed set.

Tests in a new `tests/test_difficulty.py`, with classes inheriting `CliTestCase` from `tests/test_cli.py`, plus Hypothesis (the repository's property tool) with `examples(50)` from `tests/__init__.py`:

- CLI writes: `chitty add T -d x --difficulty high` exits 0 and the file has `difficulty: high` straight after where `priority` would go (assert the frontmatter line order with `-p low` also given: `priority: low` then `difficulty: high`). `chitty edit TASK-1 --difficulty low` exits 0 and writes `difficulty: low`, and the History line names `difficulty`. `chitty edit TASK-1 --difficulty ""` removes the key. `chitty add T -d x --difficulty hard` and `chitty edit TASK-1 --difficulty hard` exit 2 and write nothing; `add` prints Click's choice error containing `'hard' is not one of 'low', 'medium', 'high'`, and `edit` prints the callback's `must be one of low, medium, high, or '' to unset` (on `main` both fail only with `No such option '--difficulty'`, which these messages tell apart) (no new file; the edited file byte-identical).
- Reads: `chitty show TASK-1` prints `difficulty: high`; `chitty show TASK-1 --json` has `"difficulty": "high"`, and `null` for a ticket without one. A ticket file written by hand with `difficulty: hard` makes `chitty check` exit non-zero with output containing `difficulty: Input should be 'low', 'medium' or 'high'` (on `main` it fails differently, with `unknown frontmatter key 'difficulty'`, since `Frontmatter` forbids extra keys).
- MCP: in `tests/test_mcp.py`'s style, the add tool with `difficulty="medium"` writes it, the edit tool with `difficulty=""` removes it, and the edit tool with `difficulty="hard"` fails with a `ToolError` whose message matches `difficulty`, leaving the file byte-identical (on `main` the unknown argument is dropped and the error is `nothing to change`, which that regex does not match).
- Property (`Edit.apply`, pure): for any ticket text drawn from `ticket_texts([TaskId("TASK", 1)])` in `tests/ticket_strategies.py` and any `d` from `("low", "medium", "high", "")`, `Edit(difficulty=d).apply(parse(text))` has `frontmatter.difficulty == (d or None)`, every other frontmatter field equal to the original's, and every section equal to the original's.
- Strategy: `_ticket_texts` in `tests/ticket_strategies.py` sometimes adds `difficulty: <one of DIFFICULTIES>`, drawn independently of `priority` and placed in `FIELD_ORDER` position (straight after the `priority` line when there is one), so the existing parse and render properties that use it cover the new field. Add a case to `tests/test_ticket_strategies.py` in the `check_find` style of `test_plan_present`, finding a drawn text containing `"\ndifficulty: "`.

All of these fail before the change: the options, the field, `Edit.difficulty` and `DIFFICULTIES` do not exist. Record each test's failure message in a note.

Out of scope: mapping difficulty to agents (`TASK-312`), guide wording (`TASK-313`), showing it in `chitty list`, and making the set configurable.

## Acceptance Criteria

- [ ] CLI and reads: the `tests/test_difficulty.py` add, edit, unset, refusal, `show`, `--json` and `chitty check` cases pass and fail before the change; record the failures in a note
- [ ] MCP: the add, unset and refusal cases pass and fail before the change
- [ ] Property and strategy: the `Edit.apply` property passes, and the new `tests/test_ticket_strategies.py` case finds a text with `difficulty`; `docs/plan/task-file.md` has the `difficulty` row; `make check` passes

## Plan

Add the specified difficulty field end-to-end. First add focused regression tests and verify they fail against current behavior, then implement model/store/CLI/MCP and strategy support, update task-file documentation, format, run make check, and commit logical changes.

## Notes

Before implementation, a Hypothesis find over ticket_texts([TaskId("TASK", 1)]) for a difficulty line failed with NoSuchExample after 2000 examples, as expected. The requested test suite and implementation remain to be written.

Runner error (agent): TASK-311 is still `doing` after 5 continuations with no new work committed; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-311`

Error output:

```text
last session: exit 0 after 25s
I verified and recorded one pre-fix failure: the ticket strategy cannot generate a `difficulty` line. The requested tests and implementation remain unfinished, so TASK-311 is still in `doing`.
```

Requeued 2026-11-23: the stall ran on `gpt-6.1-terra` (Pi session logs), before `work_model = "openai-codex/gpt-6-luna"` landed in `chitty.toml` (`0ce50010`). The branch has no code yet.

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
