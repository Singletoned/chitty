---
title: Warn in `chitty init` about agent commands without `{prompt}`
status: review
created: 2026-11-24
---

## Description

### Why

On 2026-11-23, five registered repositories (chladnify, circuitry, mullion, shelfpath, spend-model) still had `agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"`. The README says Chitty no longer manages that Pi extension and recommends `pi -p {prompt}`. `chitty init` upgraded their `chitty_version` from as old as 0.1.35 to 0.7.1 without mentioning the command. In circuitry, every `chitty run` agent from 2026-11-14 09:18 onwards (10 runs) exited in 1.5-3.6 seconds, wrote no Pi session, and was recorded only as "<ID> was unchanged".

`chitty run` still accepts a command with `{mode}` and `{id}` but no `{prompt}` (`_agent_command` in `src/chitty/run.py`, around line 989), so it gives no sign that anything is wrong.

### Change

Add a pure function `agent_command_warnings(agent_command: str | None, agent_commands: Mapping[str, str]) -> list[str]` to `src/chitty/config.py`. For `agent_command` (when not `None` and not blank) and for each `agent_commands` entry in sorted name order, when the command text does not contain `{prompt}`, it returns one line:

``<setting> has no {prompt}; Chitty no longer manages the Pi extension that `{mode}`/`{id}` commands relied on, so use a print-mode command such as `pi -p {prompt}` ``

where `<setting>` is `agent_command` or `agent_commands.<name>`, as `_agent_setting` in `src/chitty/run.py` names them. A command that contains `{prompt}` gives no line.

In `init` in `src/chitty/cli.py`, after `init_repo` returns, load the repository config (`load_repo_config(Path.cwd())`) and print each line as `warning: <line>` to stderr with `click.echo(..., err=True)`, as the other warnings in `cli.py` do. `init` still exits 0 and writes the same files as today.

Decided: warn, never refuse, and never rewrite the command (`docs/plan/direction.md`, 2026-11-23: warn generously instead of refusing). Decided: the rule is "no `{prompt}`", not "mentions `chitty.ts`": every such command depends on the retired extension or on a tool reading `{mode}`/`{id}` itself, and the warning says what to use instead. Only `chitty init` warns; `chitty run` is out of scope.

### Tests

Property, with Hypothesis (this repository's property-testing tool), in a new `tests/test_agent_command_warnings.py`: for any `agent_command` (drawn from `None`, blank strings, and text that does or does not contain `{prompt}`) and any `agent_commands` dict of up to four entries with names from `st.from_regex(r"[a-z]{1,8}", fullmatch=True)`, the result has exactly one line per non-blank command without `{prompt}`. Each line starts with that command's setting name followed by ` has no {prompt}`, `agent_command` comes first, and named entries follow in sorted order. Build the text with and without `{prompt}` by inserting `{prompt}` into a drawn string, so both kinds occur, but decide the expected result from `"{prompt}" in command`, not from how the text was built, since a drawn string can contain `{prompt}` already. Blank means `command.strip() == ""`. A stub that returns `[]` must fail the property.

Example, in `TestInit` in `tests/test_cli.py`: the shared fixture `CONFIG` in `tests/support.py` already has `agent_command = "pi --chitty-{mode} {id}"`, so run `chitty init` and assert exit code 0 and that stderr contains `warning: agent_command has no {prompt}`. Then replace that line in `chitty.toml` with `agent_command = "pi -p {prompt}"`, run `chitty init` again, and assert stderr does not contain `has no {prompt}`. Because the fixture uses the old form, every test that runs `chitty init` will now see the warning on stderr; change `CONFIG` only if an existing test that checks `init`'s exact stderr fails, and then to `pi -p {{prompt}}`, noting each test changed.

### Out of scope

Warnings in `chitty run` or `chitty check`; detecting other broken commands; the "re-run `chitty init`" warning that circuitry reported after an upgrade.

## Acceptance Criteria

- [x] A new property test in `tests/test_agent_command_warnings.py`, as the Tests section describes, shows `agent_command_warnings` returns exactly one line per non-blank command without `{prompt}`, each starting with its setting name and ` has no {prompt}`, `agent_command` first and named entries in sorted order. It fails against a stub that returns `[]`.
- [x] A new test in `TestInit` in `tests/test_cli.py` shows `chitty init` exits 0 with `warning: agent_command has no {prompt}` on stderr for the fixture's `pi --chitty-{mode} {id}` (this assertion fails today), and without `has no {prompt}` after the command is changed to `pi -p {prompt}`. `make check` passes.

## Plan

Add a pure, sorted warning builder in config and emit its results after init; first add property and CLI tests and demonstrate failure, then implement, format, and run make check.

## Notes

Requeued 2026-11-26: the last worker returned it over tool failures, not a ticket defect. Ideas from TASK-659 not in scope here: runner error detail for agents that exit within seconds (compare TASK-466, TASK-445), and the repeated re-run `chitty init` warning after an upgrade.

Before implementation, both new tests failed: the property found commands={a: 0} against an empty stub, and init emitted no warning. Decided: blank named commands produce no warning, because the Tests section and acceptance criterion explicitly exclude all blank commands.

## Summary

Init warns on nonblank agent commands without the prompt placeholder, without changing commands. Property and CLI tests failed before the fix and pass now; make check passes (1264 tests).

## History

- 2026-11-24T22:21:38Z zesty-coral-newt → backlog
- 2026-11-24T22:21:39Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:23Z zesty-coral-newt: changed notes
- 2026-11-24T23:06:21Z zesty-coral-newt: changed title, description, acceptance criteria
- 2026-11-24T23:06:21Z zesty-coral-newt backlog → cold-read
- 2026-11-24T23:07:59Z zesty-coral-newt: changed description, acceptance criteria
- 2026-11-24T23:07:59Z zesty-coral-newt cold-read → todo
- 2026-11-24T23:36:36Z zesty-quartz-ibis todo → doing
- 2026-11-24T23:40:10Z zesty-quartz-ibis: wrote the plan
- 2026-11-24T23:40:37Z zesty-quartz-ibis: changed owner, notes
- 2026-11-24T23:40:37Z zesty-quartz-ibis doing → planning
- 2026-11-26T11:37:16Z brisk-bronze-adder: changed notes
- 2026-11-26T11:37:16Z brisk-bronze-adder planning → to-plan
- 2026-11-26T11:37:23Z brisk-bronze-adder to-plan → planning
- 2026-11-26T11:37:29Z brisk-bronze-adder: replaced notes; changed owner; wrote the plan
- 2026-11-26T11:37:29Z brisk-bronze-adder planning → todo
- 2026-11-26T13:27:58Z tidy-umber-newt todo → doing
- 2026-11-26T13:32:14Z tidy-umber-newt: wrote the plan
- 2026-11-26T13:32:54Z tidy-umber-newt: changed notes
- 2026-11-26T13:36:36Z tidy-umber-newt: changed summary; ticked acceptance criteria
- 2026-11-26T13:40:26Z tidy-umber-newt doing → review
