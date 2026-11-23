---
title: "Tighten the review guide: nested bullets for the long rules"
status: review
labels:
  - untestable
owner: plucky-indigo-eel
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

## Summary

Restructured `src/chitty/roles/review.md` (839 to 816 words):

- The `design` bullet is split in two. A lead line ("set `-s planning` with cause `design`, not `doing`, when the ticket cannot guide the work:") has one nested bullet per trigger, including oversized tickets (suggest a split) and repeat `tests` failures. A "Before returning a ticket to `planning`:" bullet has nested points: keep checking; what the note contains; the branch and worktree are kept and the run stops; `blocked` for external obstacles.
- The failure-note bullet is a lead line ("every failure gets one note:") with nested points: the first line and the causes in their order; one line per criterion, with findings grouped under it; what must change and what was run; `--uncheck` and `-s doing`.
- The earlier-notes bullet is down to two sentences.
- Unchanged: the dirty-worktree stop (bullet 2), the bullet on showing each test fails without the change, and every other bullet.

Sentences removed outright, and where their point lives:
- "The dirty-worktree stop above still applies." (inspection bullet) -> the dirty-worktree stop itself, bullet 2, which applies unconditionally.
- "Gather all actionable planning issues in the `Review failed (design):` note with the verdicts below." -> the failure-note bullet: every failure, `design` included, gets one note with all of the pass's findings.
- "Report all findings from this pass together in that one note." -> "every failure gets one note" plus "Group all findings from this pass under the relevant criterion".
- "Distinguish newly discovered findings from previously reported findings that remain unresolved" -> "cite the earlier note for each finding still unresolved".

Verification: `make check`, run by `chitty edit -s review`.

## History

- 2026-11-23T12:35:02Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:57Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:45Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:41:08Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:39Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:45:10Z friendly-zinc-dormouse planning → todo
- 2026-11-23T14:35:42Z plucky-indigo-eel: changed owner
- 2026-11-23T14:35:42Z plucky-indigo-eel todo → doing
- 2026-11-23T14:43:47Z plucky-indigo-eel: changed summary
- 2026-11-23T14:43:47Z plucky-indigo-eel doing → review
