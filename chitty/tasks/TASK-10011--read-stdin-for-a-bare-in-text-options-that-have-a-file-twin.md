---
title: Read stdin for a bare `-` in text options that have a `-file` twin
status: review
labels:
  - bug
  - needs-minor
priority: medium
created: 2026-11-25
moved_from: TASK-JTE4ZH
---

## Description

Seen 2026-11-25 (trial `TASK-639`): `chitty edit TASK-639 --plan - <<EOF ... EOF` set the Plan section to a single `-` with no warning, losing the approach until the agent re-ran with `--plan-file -`. Agents reasonably expect `-` to mean stdin, as it does for every `-file` option.

Change: in `src/chitty/cli.py`, a value of exactly `-` for a text option that has a `-file` twin reads stdin, the same as passing `-` to the twin. That covers the options handled by `_text` (`--description`, `--plan`, `--set-notes`, `--summary`) and `--note` on `add` and `edit`, in `add`, `edit` and `suggest`. Do it by turning each bare `-` into its twin reading stdin before `_check_stdin_files` runs, so the existing check sees it: at most one option reads stdin per command, and each `--note -` counts once. The error keeps naming the `-file` options, as today. Giving both an option and its twin still fails as today.

Out of scope: options with no `-file` twin (for example `--title`, `--ac`); the MCP tools, which take text directly.

## Acceptance Criteria

- [x] A Hypothesis property test (`examples(...)` as elsewhere): for any text `t`, `chitty edit <ID> --plan -` with `t` on stdin stores the same Plan as `--plan-file -` with `t`; likewise for `--description`, `--summary`, `--set-notes` and `--note` on `edit`, `--description` and `--note` on `add`, and `--description` on `suggest`. Fails today: a literal `-` is stored.
- [x] Two stdin reads in one command fail with `only one file option can read stdin: <names>`, naming the `-file` options: `--plan - --note -` names `--plan-file` and `--note-file`; `--plan - --note-file -` the same; `--note - --note -` fails too. Fails today: the dashes are stored.
- [x] Regression tests: existing `-file` and stdin tests pass; `make check` passes.

## Plan

Normalize bare dashes to stdin file inputs before validation, preserving mutual exclusion and counting repeated notes. Add property and conflict regression tests, verify they fail before the fix, then format and run make check.

## Notes

Before the fix, the new property test stored a literal dash instead of stdin and the conflict cases did not report stdin conflicts. The initial suggest test also exposed a test fixture project-name issue, corrected to use an explicit path.

## Summary

Bare dashes in supported text options now read stdin, with repeated notes counted in stdin conflict checks. Property tests compare file twins across arbitrary text; conflict and mutual-exclusion tests cover errors. Verified the new behavior failed before the fix and make check passes.

## History

- 2026-11-25T22:28:33Z calm-ochre-quail → backlog
- 2026-11-25T22:28:34Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:16Z calm-ochre-quail: changed title, labels
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-JTE4ZH
- 2026-11-25T23:32:51Z calm-ochre-quail: replaced notes; changed title, priority, description, acceptance criteria
- 2026-11-25T23:32:51Z calm-ochre-quail backlog → planning
- 2026-11-25T23:33:04Z calm-ochre-quail planning → cold-read
- 2026-11-25T23:34:01Z calm-ochre-quail: changed labels, description, acceptance criteria
- 2026-11-25T23:34:01Z calm-ochre-quail cold-read → planning
- 2026-11-25T23:34:06Z calm-ochre-quail planning → todo
- 2026-11-26T00:11:43Z zesty-fawn-toad todo → doing
- 2026-11-26T00:15:38Z zesty-fawn-toad: wrote the plan
- 2026-11-26T00:17:09Z zesty-fawn-toad: changed notes
- 2026-11-26T00:24:08Z zesty-fawn-toad: changed summary; ticked acceptance criteria
- 2026-11-26T00:26:28Z zesty-fawn-toad doing → review
