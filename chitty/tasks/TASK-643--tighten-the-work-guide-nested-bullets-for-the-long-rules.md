---
title: "Tighten the work guide: nested bullets for the long rules"
status: review
labels:
  - untestable
owner: plucky-indigo-eel
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

## Summary

Restructured `src/chitty/roles/work.md` (615 to about 610 words; the gain is structure, not length):

- The `planning` bullet is now a lead line ("Set `-s planning` when the ticket cannot guide the work (but see the omission exception below):") with one nested bullet per trigger. A following bullet, "At the first such problem, stop implementation, not investigation:", has nested points: finish reading and keep checking; one note giving each issue's evidence and the decision needed, plus what could not be checked; do not work around the problem or weaken tests; keep the branch and worktree and commit partial work; ownership clears and the run stops.
- The omission bullet now starts "Omission exception:", so "(see the omission exception below)" names it. Nested bullets cover its limits, the `Decided:` note, and what goes to `planning` instead.
- Merged "Tests may create temp directories." and "Reading other branches through Git or `chitty` is fine." into one clause.
- Moved "Leave `human` tickets in `todo`..." out of the `blocked` bullet into its own bullet. The `TASK-624` budget sentence is kept word for word.

Sentences removed outright, and where their point lives:
- "At the first blocker, stop implementation, not investigation." -> reworded as the lead line of the stop bullet.
- "Before changing status, finish reading the ticket..." -> first nested point of the stop bullet.
- "On return, ownership is cleared and the run stops." -> "Setting `planning` clears ownership and stops the run."
- "This applies only to choices the ticket leaves open..." -> merged into the omission lead line.
No instruction was dropped.

Verification: `make check`, run by `chitty edit -s review`.

## History

- 2026-11-23T12:35:00Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:53Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:40Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:41:03Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:35Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:45:05Z friendly-zinc-dormouse planning → todo
- 2026-11-23T14:34:58Z plucky-indigo-eel: changed owner
- 2026-11-23T14:34:58Z plucky-indigo-eel todo → doing
- 2026-11-23T14:41:01Z plucky-indigo-eel: changed summary
- 2026-11-23T14:41:01Z plucky-indigo-eel doing → review
