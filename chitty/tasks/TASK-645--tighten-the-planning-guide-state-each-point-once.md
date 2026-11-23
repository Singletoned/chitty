---
title: "Tighten the planning guide: state each point once"
status: planning
labels:
  - untestable
owner: untestable
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

Change `src/chitty/roles/plan.md`: state each point once, in the place a planner would look for it, and tighten other long bullets, such as the sufficiency-read bullet. Leave `<!-- property-signals -->` where it is; it is replaced by `src/chitty/roles/property-signals.md` when the guide is printed.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In `--summary`, list each sentence removed outright and where its point still lives, so the reviewer can check nothing was lost.

## History

- 2026-11-23T12:35:06Z friendly-zinc-dormouse → planning
