---
title: Derive the actor from `ANTIGRAVITY_CONVERSATION_ID`
status: cold-read
created: 2026-11-24
---

## Description

### Why

`chitty` run from Google Antigravity (`agy`) fails with `cannot determine actor; set CHITTY_ACTOR or provide one of ...`, so every command needs `CHITTY_ACTOR=...` in front of it. That also stops `chitty <subcommand>` matching tool-approval prefixes. Antigravity sets `ANTIGRAVITY_CONVERSATION_ID` (stable for the conversation), plus `ANTIGRAVITY_AGENT` and `ANTIGRAVITY_TRAJECTORY_ID`. Reported from shelfpath and circuitry.

### Change

In `src/chitty/actor.py`, append `("ANTIGRAVITY_CONVERSATION_ID", "ANTIGRAVITY_CONVERSATION_ID")` to `_SESSION_IDENTITIES`, after the two `CODEX_` entries. Nothing else in `actor.py` changes: `actor()`, its error message and `pi_session_environment_missing` all read that tuple.

Decided: it goes last, so an existing harness identity wins when more than one is set (for example a Claude Code session started inside Antigravity keeps its Claude Code name). The source string is the variable name, as for the Codex entries, so the same value gives a different name than under another variable.

Also add `ANTIGRAVITY_CONVERSATION_ID` to the cleared variables in `tests/support.py` (the `excluded` set) and in `test_empty_queue_does_not_report_without_agent_identity` in `tests/test_run_error_reporter.py`, so tests run from an Antigravity session cannot pick it up. Add it to the list in `README.md` (around line 236, the paragraph on `chitty whoami`).

### Tests

No property: the input is a small fixed set of variables, each listed and tested. The new name test sets the same value, for example `conversation-1`, under `ANTIGRAVITY_CONVERSATION_ID` and under `CODEX_SESSION_ID`, and asserts the names differ. Without the change the first call raises `ChittyError`, so the test fails.

### Out of scope

`ANTIGRAVITY_AGENT` and `ANTIGRAVITY_TRAJECTORY_ID`; any detection like `pi_session_environment_missing` for Antigravity.

## Acceptance Criteria

- [ ] In `tests/test_actor.py`, `test_harness_session_names_are_stable_and_readable` includes `ANTIGRAVITY_CONVERSATION_ID`, and a new test shows that with only `ANTIGRAVITY_CONVERSATION_ID` set `actor()` returns a name that differs from the one `CODEX_SESSION_ID` gives for the same value, and that with both `CLAUDE_CODE_SESSION_ID` and `ANTIGRAVITY_CONVERSATION_ID` set it returns the Claude Code name. Both tests fail without the change.
- [ ] `test_missing_identity_fails_loudly` asserts the error names `ANTIGRAVITY_CONVERSATION_ID`, and `tests/support.py` and `tests/test_run_error_reporter.py` clear `ANTIGRAVITY_CONVERSATION_ID` wherever they clear `CODEX_SESSION_ID`.
- [ ] `README.md` lists `ANTIGRAVITY_CONVERSATION_ID` with the other harness identities, and `make check` passes.

## Notes

Suggestion origin: shelfpath

Triage 2026-11-24: TASK-689 (from circuitry) asked for the same thing; Antigravity also sets `ANTIGRAVITY_AGENT` and `ANTIGRAVITY_TRAJECTORY_ID`. `ANTIGRAVITY_CONVERSATION_ID` is the stable one to use.

## History

- 2026-11-24T22:21:22Z zesty-coral-newt → backlog
- 2026-11-24T22:21:22Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:20Z zesty-coral-newt: changed notes
- 2026-11-24T22:45:46Z zesty-coral-newt: changed title, description, acceptance criteria
- 2026-11-24T22:45:46Z zesty-coral-newt backlog → planning
- 2026-11-24T22:46:02Z zesty-coral-newt planning → cold-read
