---
title: Shrink Chitty's block in `AGENTS.md`
status: todo
priority: medium
depends_on:
  - TASK-142
parent: TASK-140
created: 2026-11-04
---

## Description

Third of three parts of `TASK-140`. `AGENTS.md` belongs to the repository, so reduce Chitty's block there to what every session needs, now that each role has its own instructions.

Rewrite `src/chitty/guide.md` to about ten lines: tasks live in `chitty/`; use the CLI or MCP and do not hand-edit task files; backticks for paths and code; `chitty --help` for commands; and which `chitty guide <role>` to run, for a person who starts an agent by hand. Anything else moves to a role file if it is not already there, so no rule is lost: check each current line and record in a note where it went or why it was dropped.

`chitty init` already replaces the block, so existing repositories pick this up through the version bump. Run it here so this repository's `AGENTS.md` matches. In this repository's own section, replace the cold-read pointer with `chitty guide plan`, and drop anything the block no longer needs.

Out of scope: the rest of a repository's `AGENTS.md`, which Chitty does not own.

## Acceptance Criteria

- [ ] `src/chitty/guide.md` is about ten lines and names `chitty guide <role>`, with a ticket note accounting for each line removed
- [ ] A test shows `chitty init` replacing an old block in an existing repository, leaving the rest of its `AGENTS.md` unchanged
- [ ] This repository's `AGENTS.md` matches and its cold-read line names `chitty guide plan`, and `__version__` is bumped above `main`'s
- [ ] `README.md` and `PLAN.md` describe where instructions live

## History

- 2026-11-04T11:56:20Z lively-panda → todo
