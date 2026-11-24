---
title: Warn in chitty init when agent_command still uses the old Pi extension
status: backlog
created: 2026-11-24
---

## Description

On 2026-11-23, five registered repositories (chladnify, circuitry, mullion, shelfpath, spend-model) still had `agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"`, although the README says Chitty no longer manages that extension and recommends `pi -p {prompt}`. `chitty init` upgraded their `chitty_version` from as old as 0.1.35 to 0.7.1 without mentioning the command; circuitry was already at 0.7.1 with the old command. Suggest: `chitty init` (and perhaps `chitty run`) prints a warning when the selected command references `chitty.ts` or uses `{mode}`/`{id}` without `{prompt}`, naming the recommended form. It should warn, not refuse (see `docs/plan/direction.md`, 2026-11-23).

## Notes

Suggestion origin: chitty

Triage 2026-11-24, merged from TASK-659 (circuitry): with the old command, 10 circuitry runs since 2026-11-14 09:18 (CIRCUIT-96/97/105/106/107) exited in 1.5-3.6 s, wrote no Pi session, and were recorded only as "<ID> was unchanged" (see `~/.local/share/chitty/usage/circuitry.jsonl`). Two further asks from TASK-659, to split off when planning: (1) when an agent exits within seconds with no commits, the runner error should give exit status, runtime and the last stderr lines (compare TASK-466 and TASK-445); (2) in circuitry, `chitty init` keeps printing "re-run `chitty init` to refresh repository setup" straight after an upgrade commit.

## History

- 2026-11-24T22:21:38Z zesty-coral-newt → backlog
- 2026-11-24T22:21:39Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:23Z zesty-coral-newt: changed notes
