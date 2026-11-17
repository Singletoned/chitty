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

## Notes

Figures, 2026-11-17 (from `pi-rtk/scripts/usage-report` and `rtk gain --daily`). Calls using `--llm-friendly` out of all calls, weeks 2026-W46 and W47: `git` 204/7950, `ls` 35/212, `grep` 0/205, `find` 6/59, `rg` 17/1061; 262 of 9487 overall (2.8%). `rtk gain --daily`, 2026-11-10 to 2026-11-17: 347 commands, 52.9K tokens of input compacted to 35.0K, 17.9K tokens saved (33.9%). Cost: the `## RTK-Friendly Command Output` section of `~/.pi/agent/AGENTS.md` is about 337 words (roughly 450 tokens) and is loaded in every Pi session; there were 565 session files since 2026-11-10, so about 250K tokens of instruction against 17.9K saved. Decision pending.

## History

- 2026-11-10T14:58:56Z jolly-heron → todo
- 2026-11-17T17:27:10Z kind-umber-toad: changed notes
