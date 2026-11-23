---
title: "Tighten the setup guide: remove repeated Pi and agent-command advice"
status: cold-read
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-640
created: 2026-11-23
---

## Description

`src/chitty/roles/setup.md` (about 570 words) has plain repeats:
- Step 3 contains "does not install or install or update a Pi extension".
- Step 3 repeats step 1's advice on Pi extensions that still autoload: inspect and remove them, then restart Pi.
- Step 3 describes configuring a command and a way to pass role instructions twice: once for Pi and once for other agents, in the same words.
- Step 4 is one long paragraph covering the first real run, failures, error reporters and the throwaway-worktree check.

Change `src/chitty/roles/setup.md`: say each point once, split step 4 into short bullets, and keep the steps' order. Keep the `chitty.toml` example and every setting name, command and placeholder (`{mode}`, `{id}`, `{prompt}`).

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In `--summary`, list each sentence removed outright and where its point still lives, so the reviewer can check nothing was lost.

## History

- 2026-11-23T12:35:10Z friendly-zinc-dormouse → planning
- 2026-11-23T12:38:04Z friendly-zinc-dormouse planning → cold-read
