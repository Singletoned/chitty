---
title: "Tighten the setup guide: remove repeated Pi and agent-command advice"
status: review
labels:
  - untestable
owner: plucky-indigo-eel
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

Change `src/chitty/roles/setup.md`: say each point once, split step 4 into short bullets, and keep the steps' order. Keep step 4's second paragraph (placeholder targets in a new repository). Keep the `chitty.toml` example and every setting name, command and placeholder (`{mode}`, `{id}`, `{prompt}`).

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In the ticket's Summary (`chitty edit --summary-file`), list each sentence removed outright and where its point still lives. That list is how the reviewer checks nothing was lost: these tickets have no acceptance criteria, and after `TASK-640` no test checks guide wording. Length is judged, not measured.

## Summary

Tightened `src/chitty/roles/setup.md` (569 to 549 words). The steps keep their order; the `chitty.toml` example, setting names, commands and placeholders are unchanged.

- Step 3 now says once, for Pi or any other agent, to configure a command and a way to pass role instructions, such as `{prompt}`. The doubled "install or install or update" is fixed.
- Step 4 is a lead sentence (check and commit config changes) followed by bullets: the throwaway-worktree check; starting a real run; what `chitty run` does in the worktree; what a run's outcome means; failures before handoff and `error_reporter`. The throwaway-worktree check is now the first bullet: it comes before declaring the runner ready, so before the first real run. The placeholder-targets paragraph is kept.

Sentences removed outright, and where their point lives:
- Step 3: "Existing copies may continue to autoload until manually inspected and removed; restart Pi after cleanup." -> step 1 (inspect `~/.pi/agent/extensions/chitty.ts`, remove it and `chitty-extension.sha256`, restart Pi). Step 3 now points there.
- Step 3: the second "For another agent, configure a command and a way to pass Chitty's role instructions, such as its prompt argument with `{prompt}`." -> merged into step 3's first sentence ("For Pi or any other agent").

Verification: `make check`, run by `chitty edit -s review`.

## History

- 2026-11-23T12:35:10Z friendly-zinc-dormouse → planning
- 2026-11-23T12:38:04Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:53Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:41:16Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:43Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:45:20Z friendly-zinc-dormouse planning → todo
- 2026-11-23T14:36:36Z plucky-indigo-eel: changed owner
- 2026-11-23T14:36:36Z plucky-indigo-eel todo → doing
- 2026-11-23T14:47:52Z plucky-indigo-eel: changed summary
- 2026-11-23T14:47:52Z plucky-indigo-eel doing → review
