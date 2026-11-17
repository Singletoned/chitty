---
title: Mark tickets owned by `untestable` with their own emoji in `chitty list`
status: review
created: 2026-11-16
---

## Description

Planners give tickets that cannot be tested the label and owner `untestable`, so the runner leaves them (see `src/chitty/roles/plan.md`). `chitty list` currently shows them like any owned ticket, as `👤`. Give them their own marker so they stand out.

In `skip_reason` in `src/chitty/selection.py` (a pure function of `TicketFacts`), return `✍️ untestable` instead of `👤 untestable` when the owner is `untestable` and `include_owner` is true, that is, in exactly the cases where it returns `👤 untestable` today. Put the owner name in a module constant `UNTESTABLE_OWNER`. `▶ running` and `👤 human` keep their precedence. Selection is unchanged, including with an owner filter. The `skipped` string in `list --json` and MCP output changes from `👤 untestable` to `✍️ untestable`; nothing parses it beyond its first word. `chitty list` prints only the first word of the reason, so the column shows `✍️`.

Files: `src/chitty/selection.py`, `tests/test_property_next.py` (Hypothesis; it already generates `TicketFacts`), a real-file CLI test for `chitty list` in a new `tests/test_list_untestable.py` inheriting `CliTestCase` from `tests/test_cli.py`, and the glyph descriptions in `docs/plan/cli.md` (glyph list and JSON `skipped` examples), `docs/plan/next-action-and-runner.md` and `README.md` (the `👤` owned-or-human line). No `needs-minor`: a cosmetic marker.

Out of scope: keying anything on the `untestable` label, and changing what `chitty next` or `chitty run` select.

## Acceptance Criteria

- [x] Hypothesis property in `tests/test_property_next.py`: add `"untestable"` to the owner values `facts_strategy` samples, and draw `include_owner` with `st.booleans()`. For any generated `TicketFacts` and `include_owner`, `skip_reason` returns `✍️ untestable` exactly when a reference copy of the pre-change rule (written in the test with the literal `"untestable"`, not `UNTESTABLE_OWNER`) returns `👤 untestable`, and otherwise returns the same value as the reference. Fails before the change.
- [x] A real-file test in `tests/test_list_untestable.py` creates a `todo` ticket owned `untestable` and another owned `alice`; `chitty list` shows `✍️` on the first line and `👤` on the second, and both titles start at the same display column as counted by `chitty.cli._columns`. Fails before the change. The three docs name `✍️`. `make check` passes.

## Plan

Add UNTESTABLE_OWNER and special-case its owner marker after the existing running/human precedence. Extend the Hypothesis property to compare against the literal pre-change skip rule across include_owner values; add a real-file list test using CliTestCase, checking markers and title columns. Update the three specified docs, then run the regression tests before the implementation where feasible, and finish with make format and make check.

## Notes

Both regression tests failed before the implementation: the property found 👤 untestable, and the CLI test found no ✍️ marker. make check passes; chitty fix reports pre-existing Markdown warnings on other tickets.

## Summary

Implemented distinct ✍️ skip marker for owner untestable, preserving running/human precedence and selection behavior. Updated property and real-file CLI coverage plus the three requested docs. Verified with make check (604 tests), chitty fix, and regression tests; commit 7c152e7. No follow-ups.

## History

- 2026-11-16T16:48:55Z open-russet-eel → planning
- 2026-11-16T16:49:07Z open-russet-eel: changed owner
- 2026-11-16T16:49:07Z open-russet-eel planning → cold-read
- 2026-11-16T16:50:22Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:50:22Z open-russet-eel cold-read → planning
- 2026-11-16T16:50:24Z open-russet-eel: changed owner
- 2026-11-16T16:50:24Z open-russet-eel planning → todo
- 2026-11-17T18:21:12Z golden-amber-quail todo → doing
- 2026-11-17T18:21:35Z golden-amber-quail: wrote the plan
- 2026-11-17T18:23:36Z golden-amber-quail: changed notes, summary; ticked acceptance criteria
- 2026-11-17T18:23:36Z golden-amber-quail doing → review
