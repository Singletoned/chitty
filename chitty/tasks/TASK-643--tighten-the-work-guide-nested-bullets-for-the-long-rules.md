---
title: "Tighten the work guide: nested bullets for the long rules"
status: cold-read
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-640
  - TASK-624
created: 2026-11-23
---

## Description

`src/chitty/roles/work.md` is about 600 words. Its bullet on returning a ticket to `planning` runs to about 170 words and bundles a list of triggers, a stop rule, what the note must contain and what to preserve. The bullets on omissions and `blocked` are also dense. Shorter, structured text is easier for weaker models to follow.

Change `src/chitty/roles/work.md`. For example, the `planning` bullet could become a lead line ("Set `-s planning` when the ticket cannot guide the work:") with one nested bullet per trigger. Follow it with a short bullet for the stop rule and the note: stop building at the first trigger but keep checking the rest; one note with each issue, its evidence and the decision needed; commit partial work; keep the branch and worktree. Merge "Tests may create temp directories." and "Reading other branches through Git or `chitty` is fine." into one clause. Keep the budget sentence `TASK-624` adds to the `-s blocked` bullet, and keep "(see omission exception below)" pointing at the right bullet.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In the ticket's Summary (`chitty edit --summary-file`), list each sentence removed outright and where its point still lives. That list is how the reviewer checks nothing was lost: these tickets have no acceptance criteria, and after `TASK-640` no test checks guide wording. Length is judged, not measured.

## History

- 2026-11-23T12:35:00Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:53Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:40Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:41:03Z friendly-zinc-dormouse: changed description
