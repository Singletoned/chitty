---
title: Give each agent session a name it can look up after compaction
status: done
priority: high
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

- [x] Chitty derives a stable readable name from the harness's session identity with no stored state; the same session gets the same name after compaction
- [x] `CHITTY_ACTOR` overrides it for humans and other tools; with no identity, writes that need one fail loudly rather than recording `unknown`
- [x] An agent can ask for its name (for example `chitty whoami`), and session-start output (`chitty inbox --pull`) prints it
- [x] The MCP server resolves the same name as shell commands in the same session
- [x] When Pi is installed, `chitty init` turns on `exposeSessionEnvironment` in Pi's settings (`~/.pi/agent/settings.json`), changing nothing else in the file and reporting the change
- [x] When `chitty guide` runs under Pi without the session environment exposed, its output explains to the agent what is missing and how to fix it
- [x] It reads the identity each harness provides (Claude Code `CLAUDE_CODE_SESSION_ID`, Pi `PI_SESSION_ID`, and Codex's equivalent or the process-ancestry fallback), with any needed setting, plugin or hook documented in `README.md` and installed or explained by `chitty init`; tests simulate each source
- [x] Subagents resolve to their parent's name by design (they inherit the parent's environment and process ancestry)

## Plan

Inspect existing identity resolution and CLI/MCP wiring; add a shared deterministic actor resolver plus `whoami` and session-start output; configure Pi session-environment exposure during init and guidance diagnostics; document supported harnesses and add focused unit tests. Run targeted tests followed by `make check`, tick verified criteria, and commit.

## Notes

Decided with the human (2026-11-01): `init` sets Pi's `exposeSessionEnvironment` itself when Pi is installed. On this machine Pi's settings live at `~/.pi/agent/settings.json` and the setting is currently absent.

Do this last in its batch: once it lands, Pi agents started before `exposeSessionEnvironment` was set cannot write until restarted (HUMAN-5).

Blocked on HUMAN-7 for the required Claude Code and Codex real-session access. The current environment exposes neither harness session identity, and Pi session environment exposure is disabled. Do not claim the cross-harness acceptance criteria without those verifications.

Unblocked with the human (2026-11-01): implement now. Real-session verification in Claude Code, Codex and Pi, including subagents, moved to HUMAN-7, which happens after this lands. An agent running in Pi cannot see Claude Code's session variables, so their absence here is expected, not a blocker.

Implemented shared identity resolution for Claude Code, Pi, and Codex session variables; verified with simulated harness environments and full `make check`.

Reviewed: independent implementation in efce9d2; verified all acceptance criteria against the code and tests, and ran make check successfully.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
- 2026-11-05T14:44:47Z vivid-wren done → archived
