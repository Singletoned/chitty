---
title: Give each agent session a name it can look up after compaction
status: blocked
priority: high
depends_on:
  - HUMAN-7
created: 2026-11-01
---

## Description

An agent must be able to tell whether it did a ticket's work, including after compaction, and Chitty must record who did what (TASK-55). Agents cannot set environment variables for their own session (each command runs in a fresh shell), so the identity must come from the harness. Plugins, hooks or harness settings are acceptable if needed. Subagents count as their parent for now (decided with the human, 2026-11-01).

Known so far:
- Claude Code sets `CLAUDE_CODE_SESSION_ID` in every shell command; it survived compaction (checked 2026-11-01: it matched the transcript file name after a compaction). `CLAUDE_CODE_CHILD_SESSION=1` is set even in a top-level session, so it does not identify subagents. `AI_AGENT` names the harness and version (`claude-code_2-1-314_agent`).
- Pi has `PI_SESSION_ID`, but only exposes it to shells when the `exposeSessionEnvironment` setting is on (TASK-57).
- Codex: not yet checked.
- Possible fallback for any harness: walk the process ancestry to the harness process and hash its PID and start time. Works for shell commands and for an MCP server the harness spawned, with no plugin, but a resumed session would get a new name.

Chitty derives a readable name (for example `peach-fox`) from a hash of the identity, so nothing is stored and the same session always gets the same name.

## Acceptance Criteria

- [ ] Chitty derives a stable readable name from the harness's session identity with no stored state; the same session gets the same name after compaction
- [ ] It works in Claude Code, Codex and Pi, each verified in a real session, with any needed setting, plugin or hook documented in `README.md` and installed or explained by `chitty init`
- [ ] `CHITTY_ACTOR` overrides it for humans and other tools; with no identity, writes that need one fail loudly rather than recording `unknown`
- [ ] An agent can ask for its name (for example `chitty whoami`), and session-start output (`chitty inbox --pull`) prints it
- [ ] The MCP server resolves the same name as shell commands in the same session
- [ ] A subagent resolves to its parent's name (verified in Claude Code)
- [ ] When Pi is installed, `chitty init` turns on `exposeSessionEnvironment` in Pi's settings (`~/.pi/agent/settings.json`), changing nothing else in the file and reporting the change
- [ ] When `chitty guide` runs under Pi without the session environment exposed, its output explains to the agent what is missing and how to fix it

## Plan

Inspect the current harness identities and existing CLI/MCP setup, implement deterministic actor resolution with `CHITTY_ACTOR` override and `whoami`, wire it into write records and session-start output, then update Pi setup/guide behavior and tests. Verify each supported harness in a real session before completing.

## Notes

Decided with the human (2026-11-01): `init` sets Pi's `exposeSessionEnvironment` itself when Pi is installed. On this machine Pi's settings live at `~/.pi/agent/settings.json` and the setting is currently absent.

Do this last in its batch: once it lands, Pi agents started before `exposeSessionEnvironment` was set cannot write until restarted (HUMAN-5).

Blocked on HUMAN-7 for the required Claude Code and Codex real-session access. The current environment exposes neither harness session identity, and Pi session environment exposure is disabled. Do not claim the cross-harness acceptance criteria without those verifications.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
