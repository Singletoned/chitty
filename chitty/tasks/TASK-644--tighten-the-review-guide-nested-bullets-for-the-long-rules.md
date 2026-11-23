---
title: "Tighten the review guide: nested bullets for the long rules"
status: planning
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-640
created: 2026-11-23
---

## Description

`src/chitty/roles/review.md` is about 840 words. Two bullets run to 120 words or more: the one on returning a ticket to `planning` (`design`), and the one on the `Review failed (<cause>):` note. Each mixes several rules in one paragraph. The bullet on comparing with earlier review notes says one idea in four sentences.

Change `src/chitty/roles/review.md`: split the two long bullets into a lead line with nested bullets, and reduce the earlier-notes bullet to one or two sentences. Keep: the dirty-worktree stop, the failure causes and their order, `--uncheck` for failed criteria, the per-criterion line format, and showing that each needed test fails without the change.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In `--summary`, list each sentence removed outright and where its point still lives, so the reviewer can check nothing was lost.

## History

- 2026-11-23T12:35:02Z friendly-zinc-dormouse → planning
