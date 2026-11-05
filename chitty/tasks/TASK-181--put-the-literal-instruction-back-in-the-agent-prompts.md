---
title: Put the literal `*` instruction back in the agent prompts
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`chittyPrompt` in `src/chitty/integrations/pi/chitty.ts` told agents: "When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`." `TASK-142` deletes `chittyPrompt` in favour of `chitty guide <mode> <ID>`, and that line is in no file under `src/chitty/roles/` nor in `src/chitty/guide.md`, so it would be lost. The other instructions in `chittyPrompt` are already in the role files.

Add the sentence to `src/chitty/roles/work.md`, `review.md` and `plan.md`, and to `src/chitty/guide.md`, because all of those agents write ticket text. Keep it to one bullet in each. `TASK-173` and `TASK-179` edit the same files, so touch only this bullet.

## Acceptance Criteria

- [ ] A test shows `chitty guide`, and `chitty guide` for each role, containing `literal single`, and `__version__` is bumped above `main`'s at the time of review

## History

- 2026-11-05T09:51:14Z mellow-newt → backlog
