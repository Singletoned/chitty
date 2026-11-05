---
title: Put the literal `*` instruction back in the agent prompts
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`chittyPrompt` in `src/chitty/integrations/pi/chitty.ts`, which `TASK-142` deleted in commit `2fc5a23`, told agents: "When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`." Agents now get their prompt from `chitty guide <mode> <ID>`, and that line is in no file under `src/chitty/roles/` nor in `src/chitty/guide.md`, so it has been lost.

Add the sentence to `src/chitty/roles/work.md`, `review.md` and `plan.md`, and to `src/chitty/guide.md`, because all of those agents write ticket text. `plan.md` and `guide.md` already have a bullet about backticks, so extend that; `work.md` and `review.md` get a new one. After editing, run `chitty init` and commit `AGENTS.md` and `chitty.toml`, because `guide.md` reaches `AGENTS.md`'s managed block only that way. `TASK-173` and `TASK-179` edit the same files, so touch only this bullet.

## History

- 2026-11-05T09:51:14Z mellow-newt → backlog
- 2026-11-05T09:53:14Z mellow-newt: changed description, acceptance criteria
