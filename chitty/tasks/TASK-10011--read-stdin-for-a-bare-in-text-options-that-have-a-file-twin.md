---
title: Read stdin for a bare `-` in text options that have a `-file` twin
status: cold-read
labels:
  - bug
priority: medium
created: 2026-11-25
moved_from: TASK-JTE4ZH
---

## Description

Seen 2026-11-25 (trial `TASK-639`): `chitty edit TASK-639 --plan - <<EOF ... EOF` set the Plan section to a single `-` with no warning, losing the approach until the agent re-ran with `--plan-file -`. Agents reasonably expect `-` to mean stdin, as it does for every `-file` option.

Change: in `src/chitty/cli.py`, a value of exactly `-` for a text option that has a `-file` twin reads stdin, the same as passing `-` to the twin. That covers the options handled by `_text` (`--description`, `--plan`, `--set-notes`, `--summary`) and `--note` on `add` and `edit`, in `add`, `edit` and `suggest`. Count such options in `_check_stdin_files`, so at most one option reads stdin per command. Giving both an option and its twin still fails as today.

Out of scope: options with no `-file` twin (for example `--title`, `--ac`); the MCP tools, which take text directly.

## Acceptance Criteria

- [ ] A Hypothesis property test (`examples(...)` as elsewhere): for any text `t`, `chitty edit <ID> --plan -` with `t` on stdin stores the same Plan as `--plan-file -` with `t`; likewise for `--description`, `--summary`, `--set-notes` and `--note` on `edit`, `--description` and `--note` on `add`, and `--description` on `suggest`. Fails today: a literal `-` is stored.
- [ ] Two options reading stdin in one command (for example `--plan - --note -`, or `--plan - --note-file -`) fail with the existing `only one file option can read stdin` message, naming both. Fails today.
- [ ] Regression tests: existing `-file` and stdin tests pass; `make check` passes.

## History

- 2026-11-25T22:28:33Z calm-ochre-quail → backlog
- 2026-11-25T22:28:34Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:16Z calm-ochre-quail: changed title, labels
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-JTE4ZH
- 2026-11-25T23:32:51Z calm-ochre-quail: replaced notes; changed title, priority, description, acceptance criteria
- 2026-11-25T23:32:51Z calm-ochre-quail backlog → planning
- 2026-11-25T23:33:04Z calm-ochre-quail planning → cold-read
