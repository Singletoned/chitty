---
title: Configure the priority list in `chitty.toml`, with `""` placing tickets that have none
status: planning
labels:
  - needs-minor
parent: TASK-607
created: 2026-11-23
---

## Description

Part of TASK-607. Decided with the person on 2026-11-23: priorities are an ordered list in `chitty.toml`, and the empty string marks where tickets with no priority rank. For example, `priorities = ["now", "soon", "", "later", "someday"]`. Named sets (such as "t-shirt sizes") are left out for now; a later ticket can add one as shorthand for a list.

Setting, in `RepoConfig` (`src/chitty/config.py`): `priorities: list[str]`, default `["high", "medium", "", "low"]`, ordered highest first. Validation raises the usual config error naming `priorities` when:

- the list does not contain exactly one `""`: `priorities must contain "" exactly once, to place tickets with no priority`;
- a name is repeated: `priorities lists '<name>' twice`;
- a name has surrounding whitespace (`name != name.strip()`) or a line break (`len(name.splitlines()) > 1`, so `\r`, `\x0b` and the other `str.splitlines` boundaries count): `priority '<name>' must be one word or phrase on one line, without surrounding spaces`.

The default changes today's order in one way. Today, a ticket with no priority ties with `medium` (`PRIORITY_RANK` in `src/chitty/selection.py` and `PRIORITY_ORDER` in `src/chitty/store.py` both give `None` and `medium` rank 1). With the default, `medium` tickets come before tickets with no priority.

Model (`src/chitty/model.py`): `Frontmatter.priority` becomes `str | None`, refusing an empty string (`priority must not be empty; remove the key instead`). A hand-written `priority: ""` is therefore a parse error, reported by `chitty check` and refused by other commands, as any invalid frontmatter is today. The model does not know the configured list.

Writes (`src/chitty/store.py`, so the CLI and MCP share them): `Repo.add` and `Repo.edit` refuse a priority that is not a non-empty configured name, raising `ChittyError` `priority '<value>' is not configured; choose from <names, comma-separated, without "">`, and nothing is written. On `edit`, `""` still unsets.

- CLI: `chitty add -p` and `chitty edit -p` become plain text options. Remove `click.Choice(PRIORITIES)` and the `_priority` callback, and leave the check to the store. The help text becomes `A configured priority; '' unsets.` (on `edit`).
- MCP: `Priority` in `src/chitty/mcp.py` becomes `str`.

`chitty check` (`src/chitty/check.py`) reports a ticket whose priority is not in the configured list as `<absolute path>: priority '<value>' is not configured`.

Ordering: replace `PRIORITY_RANK` and `PRIORITY_ORDER` with one function in `src/chitty/selection.py`, `priority_rank(priority: str | None, priorities: Sequence[str]) -> int`. It returns the index of the priority in the list, with `None` taking the index of `""`. A value that is not configured ranks after every configured one (`len(priorities)`), so a ticket that `chitty check` reports does not stop `list` or `next`. `choose` and `ordered` take a required keyword argument `priorities`, and their callers pass `repo.config.priorities`: `choose` in `next_action` in `src/chitty/store.py` (the call `choose(tuple(facts), modes=modes, owner=owner, order=order)`) and `ordered` in `src/chitty/cli.py` (`tasks = ordered(tasks, selected_statuses)`).

Display: `chitty list` shows a glyph only for the built-in names (`PRIORITY_GLYPHS`). Any other priority shows an empty priority column until TASK-633 decides how custom names are displayed; use `PRIORITY_GLYPHS.get(priority, "")`.

Docs: in `docs/plan/config.md`, add the commented line `# priorities = ["high", "medium", "", "low"] # highest first; "" places tickets with no priority`, next to `job_order`, with one sentence recording this decision. Also update the `priority` row in `docs/plan/task-file.md` (today `low|medium|high`) and the priority bullet in `docs/plan/next-action-and-runner.md` (today `high, then medium or unset, then low`) to the configured list and its order. `PRIORITIES` in `src/chitty/model.py` stays, as the built-in names that `tests/ticket_strategies.py` draws from.

Existing tests that pin the old order or the old CLI error must be updated: `tests/test_next.py` (around line 78, "unset priority ties medium"), `tests/test_property_next.py` (`TEST_PRIORITY_RANK`, `None: 1`, and every `choose(...)` call, which must pass `priorities=`), and `tests/test_cli.py` (`test_list_orders_and_displays_priority`, both its rendered-lines and its JSON order assertions, and around line 1756, the `-p urgent` error text). Also check `tests/ticket_strategies.py`, `tests/test_model.py` and `tests/test_store.py` for priority assumptions. List every test changed in a note.

Tests, in a new `tests/test_priorities_config.py`, using `RepoTestCase`. The custom config is `tests/support.py`'s `CONFIG` with the line `priorities = ["now", "soon", "", "later"]` inserted before its first `[` table line. Messages that pass through pydantic are asserted as substrings.

- Config: the default is `["high", "medium", "", "low"]`. Each of these is refused with the message above: no `""`, two `""`, `["a", "a", ""]`, `[" a", ""]`, `["a\nb", ""]`, `["a\u000bb", ""]` (written in TOML with the `\u000b` escape: TOML refuses a raw vertical tab and has no `\x` escape).
- Model: a ticket file written by hand with `priority: ""` makes `chitty.model.parse` raise with `priority must not be empty; remove the key instead`; `chitty check` exits non-zero and its output contains that message; `chitty edit TASK-1 --note x` exits non-zero, its output contains `priority must not be empty; remove the key instead`, and the file is byte-identical.
- List display, with the custom config: tickets written with `priority: now` and `priority: high` (the second by hand, as `chitty check` would report it). `chitty list` exits 0 and prints both IDs, and neither line contains any of the `PRIORITY_GLYPHS` values `⬆️`, `⏺️`, `⬇️` (on `main` the `now` ticket fails to parse, since `priority` is a literal, and the `high` line shows `⬆️`; after the change, indexing `PRIORITY_GLYPHS[fm.priority]` in `cli.py` would raise `KeyError` for `now`).
- Writes, with the custom config: `chitty add T -d x -p now` exits 0 and writes `priority: now`. `chitty add T -d x -p high` exits non-zero, its output contains `priority 'high' is not configured; choose from now, soon, later`, and no file is created. On an existing ticket, `chitty edit TASK-1 -p later` exits 0, `-p high` is refused with the same message and the file is byte-identical, and `-p ""` removes the key.
- `chitty check`: with the custom config, a ticket file written with `priority: high` is reported with the message above.
- Ordering examples, through the CLI so that `main` fails on the order and not on a signature: with the default config, add tickets with `-p low`, no priority, `-p medium` and `-p high` in that order; `chitty list --json` gives them `high`, `medium`, no priority, `low` (on `main`, no priority ties `medium` and comes first by ID). With the custom config, tickets `later`, no priority, `soon`, `now`, and one written by hand with `priority: high`: `chitty list --json` gives `now`, `soon`, no priority, `later`, `high`. `chitty next --mode work` picks a `now` ticket over an older `soon` one.
- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`: draw a list of two to five distinct names from `string.ascii_lowercase` with one `""` inserted at a drawn position, and one to eight `TicketFacts` or `StoredTask` values whose priorities are drawn from the list (with `""` meaning no priority) or from one name drawn from `string.ascii_lowercase` and filtered to be outside the list. All share one status, drawn from `todo`, `doing` and `review`; pass `statuses=(status,)` to `ordered`, and use the default order for `choose`. Each `TicketFacts` has a distinct valid `TASK-n` ID, `locked=False` and `owner=None`. `ordered` gets `StoredTask` values and `choose` gets `TicketFacts` values, built with the same drawn priorities. The test computes each expected rank itself (index in the list, the index of `""` for no priority, the list length for an unconfigured name), and does not call `priority_rank` for it. The `ordered` result is sorted by that expected rank, keeps input order for ties, and is a permutation of the input. `choose` returns a ticket of minimal expected rank, and `priority_rank` equals the expected rank for every drawn priority.
- MCP: with the custom config, the MCP add tool accepts `priority="now"`, and with `"high"` it fails with `priority 'high' is not configured; choose from now, soon, later` (assert it the way `tests/test_mcp.py` asserts other tool errors). On `main` the failure comes from the `Priority` literal instead; record that.

Run them against `main` first and record the failures in a note. The default-config example passes on `main` except for the order of `medium` against no priority.

Out of scope: `src/chitty/import_backlog.py` passes the source priority through unchanged (a name not configured is then reported by `chitty check`, as a hand-written one is); how custom priorities are displayed (TASK-633), named sets, configurable statuses (TASK-634), and `chitty init` writing the setting.

## Acceptance Criteria

- [ ] Config and model: the config cases (default, the six refusals) and the `priority: ""` model cases in `tests/test_priorities_config.py` pass, each asserting its message, and fail against `main`
- [ ] Writes, check and list: the `chitty add`/`chitty edit` write cases, the `chitty check` case and the `chitty list` display case pass and fail against `main`
- [ ] Ordering: the CLI ordering examples and the Hypothesis property pass, and the examples fail against `main`; the existing tests named above are updated and listed in a note
- [ ] MCP: the add tool accepts `priority="now"` and refuses `"high"` with the configured-name message; record the `main` failure in a note
- [ ] `docs/plan/config.md` has the `priorities` line and the decision sentence; `make check` passes

## Notes

Planner, 2026-11-23: blocker resolved by adding tests for a hand-written `priority: ""`, a line break in a name, and `chitty list` with custom names; criteria split by area. Earlier: named the tests that pin the old order and error text; the leading-emoji idea is `TASK-633`.

## History

- 2026-11-23T10:40:39Z witty-russet-gannet → backlog
- 2026-11-23T12:37:51Z witty-russet-gannet: changed title, labels, description, acceptance criteria
- 2026-11-23T12:37:51Z witty-russet-gannet backlog → cold-read
- 2026-11-23T12:38:52Z witty-russet-gannet: changed description, notes
- 2026-11-23T12:38:52Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:55:16Z witty-russet-gannet: changed notes
- 2026-11-23T13:09:00Z calm-teal-yellowhammer todo → doing
- 2026-11-23T13:11:32Z calm-teal-yellowhammer: changed owner, notes
- 2026-11-23T13:11:32Z calm-teal-yellowhammer doing → planning
- 2026-11-23T18:37:59Z witty-yellow-vole: replaced notes; changed owner, description, acceptance criteria
- 2026-11-23T18:38:18Z witty-yellow-vole: changed description
- 2026-11-23T18:38:18Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:41:09Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T18:41:09Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:41:14Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:43:55Z witty-yellow-vole: changed description
- 2026-11-23T18:43:55Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:44:00Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:44:21Z witty-yellow-vole: changed acceptance criteria
- 2026-11-23T18:44:21Z witty-yellow-vole cold-read → planning
