---
title: Check whether Pi agents use `pi-rtk` output
status: todo
created: 2026-11-10
---

## Description

On 2026-11-10 `pi-rtk` moved from the login shell PATH to Pi only, and agents were told about `--llm-friendly` for the first time. Before that, 892 Pi sessions had zero uses: the instruction had never been installed.

Setup: `shellCommandPrefix` in `~/.pi/agent/settings.json` defines `git`, `ls`, `grep`, `find` and `rg` as functions calling the shims, so only commands the agent types go through them; the instruction text is at the end of `~/.pi/agent/AGENTS.md`.

On or after 2026-11-17, run `~/src/singletoned/pi-rtk/scripts/usage-report` (calls with the marker per week, from 2026-W46) and `rtk gain --daily` (tokens saved). Then decide: keep it, improve the instruction, or remove the prefix and the AGENTS.md section.

## Acceptance Criteria

- [ ] A note records the usage and savings figures and the decision: keep, change, or remove.

## History

- 2026-11-10T14:58:56Z jolly-heron → todo
