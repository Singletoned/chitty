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

`src/chitty/roles/review.md` is about 840 words. Two bullets are long: the one on returning a ticket to `planning` (`design`, about 185 words) and the one on the `Review failed (<cause>):` note (about 120). Each mixes several rules in one paragraph. The bullet on comparing with earlier review notes says one idea in three sentences. Some points repeat: the dirty-worktree stop is restated in the inspection bullet, and "all findings in one note" appears in both long bullets.

Change `src/chitty/roles/review.md`: split the two long bullets into a lead line with nested bullets, and reduce the earlier-notes bullet to one or two sentences. Keep: the dirty-worktree stop, the failure causes and their order, `--uncheck` for failed criteria, the per-criterion line format, and showing that each needed test fails without the change.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In the ticket's Summary (`chitty edit --summary-file`), list each sentence removed outright and where its point still lives. That list is how the reviewer checks nothing was lost: these tickets have no acceptance criteria, and after `TASK-640` no test checks guide wording. Length is judged, not measured.

## History

- 2026-11-23T12:35:02Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:57Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:45Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:41:08Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:39Z friendly-zinc-dormouse cold-read → planning
