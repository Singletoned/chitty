---
title: Let agents leave observations for the next retro
status: backlog
priority: high
depends_on:
  - TASK-104
parent: TASK-106
created: 2026-11-03
---

## Description

Agents notice things nobody asks them about: a misleading doc, a slow setup, a criterion they had to guess at, a prompt rule that got in the way. Failure causes only capture what a reviewer rejected, so this evidence is lost when the session ends. Give agents a way to pass it to the next retro without proposing work.

Observations live on the ticket being worked on. That ticket is already on the agent's branch with one writer, so nothing touches a shared file, and the observation arrives with its context. A shared retro ticket would conflict across branches, and `chitty suggest` turns everything into a backlog ticket.

Proposed form, starting with a convention: a note starting `Retro: `, saying what happened and what it cost, findable with `grep -r '^Retro: ' chitty/tasks`. This matches `Review failed (<cause>): ...`. If the first two retros find observations useful, promote them to a dedicated section and flag (`TASK-111` decides this with the other structured fields).

Boundary: if you know what should change, use `chitty add` or `chitty suggest`. If you only noticed something, leave an observation. A problem with Chitty itself seen from another repository still goes through `chitty suggest chitty`.

Observations are optional. Agents asked for feedback tend to invent some, so the prompt must say that having none is normal, and the retro discards by default and acts on recurrence.

## Acceptance Criteria

- [ ] `src/chitty/guide.md` says when and how to leave a `Retro: ` note, that one is optional, and how it differs from `chitty add` and `chitty suggest`
- [ ] The Pi work and review prompts ask once, at the end of a stage, with a Node test covering the wording
- [ ] `PLAN.md` adds observations to the feedback loops and says a retro reads every `Retro: ` note since the last retro and records which ones led to a change
- [ ] `__version__` is bumped

## History

- 2026-11-03T10:45:23Z lively-panda → backlog
