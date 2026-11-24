---
title: Warn in chitty init when agent_command still uses the old Pi extension
status: backlog
created: 2026-11-24
---

## Description

On 2026-11-23, five registered repositories (chladnify, circuitry, mullion, shelfpath, spend-model) still had `agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"`, although the README says Chitty no longer manages that extension and recommends `pi -p {prompt}`. `chitty init` upgraded their `chitty_version` from as old as 0.1.35 to 0.7.1 without mentioning the command; circuitry was already at 0.7.1 with the old command. Suggest: `chitty init` (and perhaps `chitty run`) prints a warning when the selected command references `chitty.ts` or uses `{mode}`/`{id}` without `{prompt}`, naming the recommended form. It should warn, not refuse (see `docs/plan/direction.md`, 2026-11-23).

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:38Z zesty-coral-newt → backlog
- 2026-11-24T22:21:39Z zesty-coral-newt: changed notes
