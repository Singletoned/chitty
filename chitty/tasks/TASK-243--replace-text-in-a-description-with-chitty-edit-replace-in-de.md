---
title: Replace text in a description with `chitty edit --replace-in-description`
status: backlog
created: 2026-11-10
---

## Description

Planners mostly make small replacements inside long descriptions. `-d` and `--description-file` replace the whole section, so planners script `chitty show --json`, a string replace and `--description-file`, and often hit whitespace or line-wrap mismatches.

Decisions:

- Add `chitty edit ID --replace-in-description OLD NEW`, which replaces OLD with NEW in the Description section. It fails, changing nothing, unless OLD occurs exactly once, and the error says how many times it occurred. Exact text, as in agents' own file-edit tools, rather than line numbers, which shift when a formatter rewraps the text.
- It cannot be combined with `-d` or `--description-file`.
- Add it to `Edit` in `src/chitty/store.py` and as a parameter of the MCP `edit` tool in `src/chitty/mcp.py`.
- Update the CLI section of `PLAN.md`.

Out of scope: the same for criteria (`--set-ac` covers them), plan or notes.

## Acceptance Criteria

- [ ] A test replaces a phrase occurring once in the Description; only that text changes.
- [ ] Tests show OLD occurring zero times and twice each fails with an error naming the count, leaving the file unchanged.
- [ ] A test in `tests/test_mcp.py` does the replacement through the MCP `edit` tool.

## History

- 2026-11-10T14:08:43Z jolly-heron → backlog
