---
title: Configure the priority list in `chitty.toml`, with `""` placing tickets that have none
status: doing
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
- a name has surrounding whitespace or a line break: `priority '<name>' must be one word or phrase on one line, without surrounding spaces`.

The default changes today's order in one way. Today, a ticket with no priority ties with `medium` (`PRIORITY_RANK` in `src/chitty/selection.py` and `PRIORITY_ORDER` in `src/chitty/store.py` both give `None` and `medium` rank 1). With the default, `medium` tickets come before tickets with no priority.

Model (`src/chitty/model.py`): `Frontmatter.priority` becomes `str | None`, refusing an empty string (`priority must not be empty; remove the key instead`). A hand-written `priority: ""` is therefore a parse error, reported by `chitty check` and refused by other commands, as any invalid frontmatter is today. The model does not know the configured list.

Writes (`src/chitty/store.py`, so the CLI and MCP share them): `Repo.add` and `Repo.edit` refuse a priority that is not a non-empty configured name, raising `ChittyError` `priority '<value>' is not configured; choose from <names, comma-separated, without "">`, and nothing is written. On `edit`, `""` still unsets.

- CLI: `chitty add -p` and `chitty edit -p` become plain text options. Remove `click.Choice(PRIORITIES)` and the `_priority` callback, and leave the check to the store. The help text becomes `A configured priority; '' unsets.` (on `edit`).
- MCP: `Priority` in `src/chitty/mcp.py` becomes `str`.

`chitty check` (`src/chitty/check.py`) reports a ticket whose priority is not in the configured list as `<absolute path>: priority '<value>' is not configured`.

Ordering: replace `PRIORITY_RANK` and `PRIORITY_ORDER` with one function in `src/chitty/selection.py`, `priority_rank(priority: str | None, priorities: Sequence[str]) -> int`. It returns the index of the priority in the list, with `None` taking the index of `""`. A value that is not configured ranks after every configured one (`len(priorities)`), so a ticket that `chitty check` reports does not stop `list` or `next`. `choose` and `ordered` take a required keyword argument `priorities`, and their callers pass `repo.config.priorities`.

Display: `chitty list` shows a glyph only for the built-in names (`PRIORITY_GLYPHS`). Any other priority shows an empty priority column until TASK-633 decides how custom names are displayed; use `PRIORITY_GLYPHS.get(priority, "")`.

Docs: in `docs/plan/config.md`, add the commented line `# priorities = ["high", "medium", "", "low"] # highest first; "" places tickets with no priority`, next to `job_order`, with one sentence recording this decision.

Existing tests that pin the old order or the old CLI error must be updated: `tests/test_next.py` (around line 78, "unset priority ties medium"), `tests/test_property_next.py` (`TEST_PRIORITY_RANK`, `None: 1`), and `tests/test_cli.py` (around line 1093, the expected list order, and around line 1756, the `-p urgent` error text). Also check `tests/ticket_strategies.py`, `tests/test_model.py` and `tests/test_store.py` for priority assumptions. List every test changed in a note.

Tests, in a new `tests/test_priorities_config.py`, using `RepoTestCase`. The custom config is `tests/support.py`'s `CONFIG` with the line `priorities = ["now", "soon", "", "later"]` inserted before its first `[` table line. Messages that pass through pydantic are asserted as substrings.

- Config: the default is `["high", "medium", "", "low"]`. Each of these is refused with the message above: no `""`, two `""`, `["a", "a", ""]`, `[" a", ""]`.
- Writes, with the custom config: `chitty add T -d x -p now` exits 0 and writes `priority: now`. `chitty add T -d x -p high` exits non-zero, its output contains `priority 'high' is not configured; choose from now, soon, later`, and no file is created. On an existing ticket, `chitty edit TASK-1 -p later` exits 0, `-p high` is refused with the same message and the file is byte-identical, and `-p ""` removes the key.
- `chitty check`: with the custom config, a ticket file written with `priority: high` is reported with the message above.
- Ordering examples: with the default list, `ordered` puts the tickets `high`, `medium`, no priority, `low` in that order whatever the input order. With the custom list, `now`, `soon`, no priority, `later`, and a ticket with `priority: high` last. `choose` picks the `now` ticket over an older `soon` one.
- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`: draw a list of two to five distinct names from `string.ascii_lowercase` with one `""` inserted at a drawn position, and one to eight `TicketFacts` or `StoredTask` values whose priorities are drawn from the list (with `""` meaning no priority) or from one name drawn from `string.ascii_lowercase` and filtered to be outside the list. All share one status. `ordered` gets `StoredTask` values and `choose` gets `TicketFacts` values, built with the same drawn priorities. The `ordered` result is sorted by `priority_rank`, keeps input order for ties, and is a permutation of the input. `choose` returns a ticket of minimal rank.
- MCP: with the custom config, the MCP add tool accepts `priority="now"`, and with `"high"` it fails with `priority 'high' is not configured; choose from now, soon, later` (assert it the way `tests/test_mcp.py` asserts other tool errors). On `main` the failure comes from the `Priority` literal instead; record that.

Run them against `main` first and record the failures in a note. The default-config example passes on `main` except for the order of `medium` against no priority.

Out of scope: how custom priorities are displayed (TASK-633), named sets, configurable statuses (TASK-634), and `chitty init` writing the setting.

## Acceptance Criteria

- [ ] The config, write, `chitty check`, ordering, property and MCP tests in `tests/test_priorities_config.py` pass; each fails against `main`. Record both runs in a note
- [ ] `docs/plan/config.md` has the `priorities` line and the decision sentence; `make check` passes

## Notes

Planner, 2026-11-23: a cold read found nothing serious. Named the existing tests that pin the old order and error text, said what a hand-written `priority: ""` does, and fixed the property's types and unconfigured-name generator, the config placement in `CONFIG`, the MCP assertion and substring matching.

Planner, 2026-11-23: the person proposed leading emoji in `priorities` entries (default `["⬆️high", "⏺️medium", "", "⬇️low"]`). That is TASK-633, which builds on this ticket; nothing changes here.

## History

- 2026-11-23T10:40:39Z witty-russet-gannet → backlog
- 2026-11-23T12:37:51Z witty-russet-gannet: changed title, labels, description, acceptance criteria
- 2026-11-23T12:37:51Z witty-russet-gannet backlog → cold-read
- 2026-11-23T12:38:52Z witty-russet-gannet: changed description, notes
- 2026-11-23T12:38:52Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:55:16Z witty-russet-gannet: changed notes
- 2026-11-23T13:09:00Z calm-teal-yellowhammer todo → doing
