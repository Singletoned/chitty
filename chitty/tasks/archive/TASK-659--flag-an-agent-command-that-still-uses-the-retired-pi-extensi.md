---
title: Flag an agent_command that still uses the retired Pi extension
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

In the circuitry repo, `chitty.toml` still has `agent_command = "env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"`. The chitty README now says Chitty no longer manages that extension and to use `pi -p {prompt}`. Since 2026-11-14 09:18 every circuitry `chitty run` agent (10 runs, CIRCUIT-96/97/105/106/107, last on 2026-11-22 22:12-22:18) exited after 1.5-3.6 seconds (see `~/.local/share/chitty/usage/circuitry.jsonl`), wrote no Pi session file, and was recorded only as "<ID> was unchanged; only committed changes are visible to `chitty run`". Runs before that, with the same command, took 70-390 seconds and worked. Sibling projects (chitty, taidy, echonomicon) use `pi -p ... {prompt}` and ran fine at the same time. Suggested fixes: have `chitty init` or `chitty check` warn when `agent_command` uses `--chitty-{mode}` or `chitty.ts`; and when an agent exits within a few seconds with no commits, say so in the runner error (exit status, runtime, last stderr lines) instead of only "unchanged". `chitty init` also keeps printing "re-run `chitty init` to refresh repository setup" in circuitry even straight after an upgrade commit.

## Notes

Suggestion origin: circuitry

Duplicate of TASK-675 (warn about an `agent_command` that still uses the retired Pi extension); its evidence and two extra asks are recorded there.

## History

- 2026-11-24T22:21:22Z zesty-coral-newt → backlog
- 2026-11-24T22:21:23Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:25Z zesty-coral-newt: changed labels, notes
- 2026-11-24T22:41:16Z zesty-coral-newt backlog → archived
