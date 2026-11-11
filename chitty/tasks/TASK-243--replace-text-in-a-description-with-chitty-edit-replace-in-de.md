---
title: Replace text in a description with `chitty edit --replace-in-description`
status: done
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

Add a regression test that proves replacement records `changed description` in History, run it to confirm the failure, then fix the edit-history classification and run focused plus full checks.

## Notes

Cold read 1 (Haiku): fixed: empty OLD counted len+1 matches; now rejected. Decided and stated: match against the pre-edit Description; History `changed description`; allowed in review, like `-d`; emptying keeps the existing required-section error. Left to the worker: exact combination error text and the MCP parameter shape. Possible starting point: `git diff main...refs/cold-read/TASK-243/1`; check it against the current criteria, not trust it.

Implementation verified: focused CLI and MCP tests pass; make format and make check pass (425 Python tests and Node tests). Exact multiplicity and empty OLD validation happen before writing, preserving files on errors. The regression tests were run after implementation rather than against the unfixed behavior.

Review failed (integration): merging `main` conflicts in `tests/test_mcp.py`.

Merged main and resolved the test_mcp.py conflict by retaining both the description-replacement and notes-replacement tests. make format && make check passes (438 Python tests and Node tests); working tree clean.

Review failed (tests): Add a regression test and fix History for description replacement. A throwaway CliTestCase ran add followed by edit --replace-in-description and printed `description: New phrase` and `history: - 2026-11-10T18:14:52Z test-agent → todo`; the required `changed description` event is missing. make format && make check passed (438 Python tests and Node tests). Criterion 1 is marked failed because the replacement lacks its required History event.
1: fail - Replacement does not record changed description in History.
2: pass - CLI test verifies counts and unchanged files.
3: pass - MCP test exercises replacement.

Added a store regression test for the missing History event. It failed before the fix (History contained only the initial status event) and passes after `_history_action` classifies replacement edits as changed description. `make format` passes; `make check` has 438 passing tests and one unrelated existing failure: `test_warning_is_in_every_generated_guide` finds the generated guide differs from the source. Committed as 47eb138.

Reviewed: make format && make check pass (446 Python tests and Node tests). A throwaway test verified conflicting description options, empty result and editing in review.
1: pass - CLI test replaces the unique phrase and checks the resulting description; History regression passes.
2: pass - CLI test checks zero and two matches and empty OLD, preserving the file.
3: pass - MCP tool test replaces a phrase in the description.

## Summary

Handoff: description replacements now record `changed description` in History; regression test added. Verification: focused regression passes; format passes; full check blocked by unrelated generated-guide mismatch (`test_warning_is_in_every_generated_guide`; 438 other tests pass). Follow-up: resolve that guide mismatch.

## History

- 2026-11-10T14:08:43Z jolly-heron → backlog
- 2026-11-10T14:19:32Z jolly-heron: changed description, acceptance criteria, notes
- 2026-11-10T14:19:33Z jolly-heron backlog → todo
- 2026-11-10T17:16:36Z sunny-puffin todo → doing
- 2026-11-10T17:16:54Z sunny-puffin: wrote the plan
- 2026-11-10T17:19:34Z sunny-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-10T17:19:34Z sunny-puffin doing → review
- 2026-11-10T18:08:26Z friendly-newt: changed notes
- 2026-11-10T18:08:26Z friendly-newt review → doing
- 2026-11-10T18:12:02Z nimble-badger: changed notes, summary
- 2026-11-10T18:12:02Z nimble-badger doing → review
- 2026-11-10T18:15:19Z zesty-ibis: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-10T18:15:19Z zesty-ibis review → doing
- 2026-11-10T21:06:49Z sunny-adder: wrote the plan
- 2026-11-10T21:09:04Z sunny-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-10T21:09:04Z sunny-adder doing → review
- 2026-11-10T22:19:50Z mellow-jay: changed notes; ticked acceptance criteria
- 2026-11-10T22:19:50Z mellow-jay review → done
