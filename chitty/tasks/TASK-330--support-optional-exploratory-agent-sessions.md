---
title: Support optional exploratory agent sessions
status: planning
priority: medium
created: 2026-11-14
---

## Description

Agents are currently shaped around Chitty ticket work and review flows. Add a PoC/exploratory mode for sessions where an agent may use Chitty when useful, but is not required to claim, update, or complete a ticket. Existing work and review workflows must retain their current requirements.

## Acceptance Criteria

- [ ] A user can start an agent in an explicitly named exploratory or PoC mode without supplying a Chitty ticket ID.
- [ ] The exploratory mode tells the agent that Chitty use is optional and does not require ticket lifecycle changes for the session to succeed.
- [ ] Existing work and review modes continue to require their current ticket and lifecycle behavior.
- [ ] Automated tests cover exploratory-mode invocation and prove that the existing work and review paths are unchanged.

## Notes

Cold read outcome: keep this ticket in `planning` until the invocation and lifecycle are decided. The current ticket does not specify whether PoC mode is a new `chitty run` mode, a named `[agent_commands]` command, or a separate agent invocation; whether it uses the current checkout or a temporary worktree; whether setup/check/cleanup/commits apply; how forwarded arguments, timeout, model selection, continuation, and failures behave; or what observable event defines success without a ticket status change. It also needs one canonical mode name (`exploratory` or `poc`, or explicitly defined aliases). Likely implementation surfaces are `src/chitty/cli.py`, `src/chitty/run.py`, `src/chitty/config.py`, `src/chitty/store.py`, the role guide, runner docs, and runner tests.

## History

- 2026-11-14T13:39:35Z jolly-umber-badger → planning
- 2026-11-14T13:40:56Z jolly-umber-badger: changed notes
