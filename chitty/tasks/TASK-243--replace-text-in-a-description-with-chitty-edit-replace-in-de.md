---
title: Replace text in a description with `chitty edit --replace-in-description`
status: review
created: 2026-11-10
---

## Description

Planners mostly make small replacements inside long descriptions. `-d` and `--description-file` replace the whole section, so planners script `chitty show --json`, a string replace and `--description-file`, and often hit whitespace or line-wrap mismatches.

Decisions:

- Add `chitty edit ID --replace-in-description OLD NEW`, which replaces OLD with NEW in the Description section. It fails, changing nothing, unless OLD occurs exactly once, and the error says how many times it occurred. Exact text, as in agents' own file-edit tools, rather than line numbers, which shift when a formatter rewraps the text.
- It cannot be combined with `-d` or `--description-file`.
- OLD is matched against the Description as it was before this edit. An empty OLD is rejected with `ChittyError`.
- It behaves like `-d` otherwise: History records `changed description`, it is allowed in review, and a replacement that empties the Description fails with the existing required-section error.
- Add it to `Edit` in `src/chitty/store.py` and as a parameter of the MCP `edit` tool in `src/chitty/mcp.py`.
- Update the CLI section of `PLAN.md`.

Out of scope: the same for criteria (`--set-ac` covers them), plan or notes.

## Acceptance Criteria

- [x] A test replaces a phrase occurring once in the Description; only that text changes.
- [x] Tests show OLD occurring zero times and twice each fails with an error naming the count, and an empty OLD fails; each leaves the file unchanged.
- [x] A test in `tests/test_mcp.py` does the replacement through the MCP `edit` tool.

## Plan

Add replacement semantics to store.Edit, validate exclusivity with whole-description replacement and unique nonempty old text, and preserve existing description validation/history behavior. Expose the option in CLI and MCP, add focused store/CLI/MCP tests including unchanged files on errors, and document the CLI option in PLAN.md. Run regression tests before implementation where practical, then format/check.

## Notes

Cold read 1 (Haiku): fixed: empty OLD counted len+1 matches; now rejected. Decided and stated: match against the pre-edit Description; History `changed description`; allowed in review, like `-d`; emptying keeps the existing required-section error. Left to the worker: exact combination error text and the MCP parameter shape. Possible starting point: `git diff main...refs/cold-read/TASK-243/1`; check it against the current criteria, not trust it.

Implementation verified: focused CLI and MCP tests pass; make format and make check pass (425 Python tests and Node tests). Exact multiplicity and empty OLD validation happen before writing, preserving files on errors. The regression tests were run after implementation rather than against the unfixed behavior.

## Summary

Implemented --replace-in-description OLD NEW through the CLI, MCP, and shared store; documented it in PLAN.md. Verification: focused CLI/MCP tests and make format && make check pass. No follow-ups.

## History

- 2026-11-10T14:08:43Z jolly-heron → backlog
- 2026-11-10T14:19:32Z jolly-heron: changed description, acceptance criteria, notes
- 2026-11-10T14:19:33Z jolly-heron backlog → todo
- 2026-11-10T17:16:36Z sunny-puffin todo → doing
- 2026-11-10T17:16:54Z sunny-puffin: wrote the plan
- 2026-11-10T17:19:34Z sunny-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-10T17:19:34Z sunny-puffin doing → review
