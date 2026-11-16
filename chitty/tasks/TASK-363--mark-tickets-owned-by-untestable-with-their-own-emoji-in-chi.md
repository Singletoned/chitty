---
title: Mark tickets owned by `untestable` with their own emoji in `chitty list`
status: cold-read
owner: open-russet-eel
created: 2026-11-16
---

## Description

Planners give tickets that cannot be tested the label and owner `untestable`, so the runner leaves them (see `src/chitty/roles/plan.md`). `chitty list` currently shows them like any owned ticket, as `👤`. Give them their own marker so they stand out.

In `skip_reason` in `src/chitty/selection.py` (a pure function of `TicketFacts`), return `✍️ untestable` instead of `👤 untestable` when the owner is `untestable` and the owner is otherwise reported, that is, in exactly the cases where it returns `👤 untestable` today. Put the owner name in a module constant `UNTESTABLE_OWNER`. `▶ running` and `👤 human` keep their precedence. Selection is unchanged: such tickets are already skipped because they have an owner. `chitty list` prints only the first word of the reason, so the column shows `✍️`.

Files: `src/chitty/selection.py`, `tests/test_property_next.py` (Hypothesis; it already generates `TicketFacts`), and a real-file CLI test for `chitty list` in a new `tests/test_list_untestable.py`.

Out of scope: keying anything on the `untestable` label, and changing what `chitty next` or `chitty run` select.

## Acceptance Criteria

- [ ] Hypothesis property in `tests/test_property_next.py`: for any generated `TicketFacts` and `include_owner`, `skip_reason` returns `✍️ untestable` exactly when the pre-change rule would return `👤 untestable`, and otherwise returns the same value as the pre-change rule (write the old rule as a reference function in the test). The generator must produce owners `untestable`, `human`, other names and `None`, locked and unlocked, and the `human` context. Fails before the change.
- [ ] A real-file test in `tests/test_list_untestable.py` creates a `todo` ticket owned `untestable` and another owned `alice`; `chitty list` shows `✍️` on the first line and `👤` on the second, and both titles start at the same column. Fails before the change. `make check` passes.

## History

- 2026-11-16T16:48:55Z open-russet-eel → planning
- 2026-11-16T16:49:07Z open-russet-eel: changed owner
- 2026-11-16T16:49:07Z open-russet-eel planning → cold-read
