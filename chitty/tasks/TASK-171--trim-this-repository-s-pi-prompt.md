---
title: Trim this repository's Pi prompt
status: todo
priority: high
owner: human
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 4. About 15,400 tokens go out before a session reads its task, 21% of spend. `TASK-136` has since removed other extensions through `--no-extensions`, so some of that has already gone, and the analysis predates it. Most of what is left is `context-mode`'s tools and skill listings.

This is the planning session's to do, not a worker's: the check needs a real session, and `chitty run` picks its own ticket, so a worker could not nest one. The planning session commits the change on `main`, the human's next `chitty run` uses it, and the planning session compares that session's first call with a recent one's, from their session files. This is configuration, with no change to Chitty's code. Add these to `agent_command` in `chitty.toml`, keeping the `env -u ... uv run --no-sync` prefix and `context-mode`:

`--no-skills --skill ~/.pi/agent/skills/python-dev --exclude-tools ctx_fetch_and_index,ctx_index,ctx_purge,ctx_upgrade,ctx_insight,ctx_stats,ctx_doctor`

The other tools in the doc's list came from extensions that no longer load. Six of the names are confirmed in `context-mode`'s Pi adapter, and `ctx_insight` only in its server, so check that an unknown name does no harm. Do not remove a tool sessions used more than rarely. `TASK-176`'s trial of `context-mode` as a whole is separate.

## Acceptance Criteria

- [ ] A note records a real session's first-call input tokens before and after, that the session finished its ticket, and that `--no-skills` removed nothing agents used

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. A worker could not do the real-session check, so this moved to the planning session and the human. It confirmed the doc's other tools come from extensions that no longer load, and that nothing relies on a skill.

## History

- 2026-11-04T21:41:06Z mellow-newt → backlog
- 2026-11-04T21:41:36Z mellow-newt: changed description
- 2026-11-04T21:44:22Z mellow-newt: changed priority, owner, description, acceptance criteria, notes
- 2026-11-04T21:44:23Z mellow-newt backlog → todo
