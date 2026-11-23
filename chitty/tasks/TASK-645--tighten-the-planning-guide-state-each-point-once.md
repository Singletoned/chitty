---
title: "Tighten the planning guide: state each point once"
status: review
labels:
  - untestable
owner: plucky-indigo-eel
depends_on:
  - TASK-640
  - TASK-615
created: 2026-11-23
---

## Description

`src/chitty/roles/plan.md` is the longest guide, at about 1,300 words, and some points appear more than once:
- "Say which test must fail without the fix" appears twice: in the bullet starting "Ask of each criterion" and as its own bullet just before `<!-- property-signals -->`.
- Splitting advice appears three times: about five criteria in the bullet starting "Write tickets that a fresh agent", the third-read split in "After a fix that changes", and "Split rather than exceed about five criteria" in "Before moving to `todo`".
- The bullet on wrong versions of existing code and the next bullet, on running generator recipes against existing code, both cover code that already exists and could be one bullet with nested points.

Change `src/chitty/roles/plan.md`, as it stands after `TASK-615` lands:
- Keep "say which test must fail without the fix" in the "Ask of each criterion" bullet, with the reason "a nearby test may already pass", and delete the standalone bullet.
- Keep every split rule in "Write tickets that a fresh agent" (one to three criteria per outcome, err on the side of splitting, the `chitty check` warning, about five checks per criterion) and the third-read split in "After a fix that changes" (a different trigger); drop "Split rather than exceed about five criteria" from "Before moving to `todo`".
- Merge the wrong-versions bullet and the generator-recipe bullet into one bullet with nested points.
- Tighten the sufficiency-read bullet. Other long bullets are the worker's judgement. Leave `<!-- property-signals -->` where it is; it is replaced by `src/chitty/roles/property-signals.md` when the guide is printed.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In the ticket's Summary (`chitty edit --summary-file`), list each sentence removed outright and where its point still lives. That list is how the reviewer checks nothing was lost: these tickets have no acceptance criteria, and after `TASK-640` no test checks guide wording. Length is judged, not measured.

## Summary

Tightened `src/chitty/roles/plan.md` (1,325 to 1,309 words), as it stands after `TASK-615`:

- "Ask of each criterion" now ends "say which test must fail without the fix, because a nearby test may already pass."
- Merged the wrong-versions bullet and the generator-recipe bullet into one. Its lead line is "When the code a ticket tests already exists, a stub cannot show the tests fail without the change:", with nested points for wrong versions, example-based tests, property tests, and running the generator recipes before the cold read.
- Tightened the sufficiency-read bullet's wording. Its steps are the same: each criterion and the whole ticket, a counterexample, a distinguishing test with its observable result, criterion wording, prefer a property, no speculative features, ask about odd behaviour.
- `<!-- property-signals -->` has not moved. The split rules in "Write tickets that a fresh agent" and the third-read split are unchanged.

Sentences removed outright, and where their point lives:
- Standalone bullet "Say which test must fail without the fix, because a nearby test may already pass." -> the "Ask of each criterion" bullet, with its reason.
- "Split rather than exceed about five criteria." (in "Before moving to `todo`") -> "`chitty check` warns above five criteria; split larger work." in "Write tickets that a fresh agent".
- "When the code already exists, run each specified generator recipe..." -> reworded as the last nested point of the merged existing-code bullet.

Verification: `make check`, run by `chitty edit -s review`.

## History

- 2026-11-23T12:35:06Z friendly-zinc-dormouse → planning
- 2026-11-23T12:38:01Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:49Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:41:12Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:32Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:32Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:45:15Z friendly-zinc-dormouse planning → todo
- 2026-11-23T14:36:10Z plucky-indigo-eel: changed owner
- 2026-11-23T14:36:10Z plucky-indigo-eel todo → doing
- 2026-11-23T14:45:52Z plucky-indigo-eel: changed summary
- 2026-11-23T14:45:52Z plucky-indigo-eel doing → review
