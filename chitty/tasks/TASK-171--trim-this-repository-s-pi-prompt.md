---
title: Trim this repository's Pi prompt
status: backlog
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 4. About 15,400 tokens go out before a session reads its task, 21% of spend. `TASK-136` has since removed other extensions through `--no-extensions`, so some of that has already gone, and the analysis predates it. Most of what is left is `context-mode`'s tools and skill listings.

This is configuration, with no change to Chitty's code. Add these to `agent_command` in `chitty.toml`, keeping the `env -u ... uv run --no-sync` prefix and `context-mode`:

`--no-skills --skill ~/.pi/agent/skills/python-dev --exclude-tools ctx_fetch_and_index,ctx_index,ctx_purge,ctx_upgrade,ctx_insight,ctx_stats,ctx_doctor`

The other tools in the doc's list came from extensions that no longer load. Do not remove a tool sessions used more than rarely. `TASK-171`'s trial of `context-mode` as a whole is separate.

## Acceptance Criteria

- [ ] A real `chitty run` session is checked to start and do its work with these flags, and a note records its first call's input tokens with and without them, from its session file

## History

- 2026-11-04T21:41:06Z mellow-newt → backlog
