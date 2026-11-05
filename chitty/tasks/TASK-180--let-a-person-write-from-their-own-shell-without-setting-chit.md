---
title: Let a person write from their own shell without setting `CHITTY_ACTOR`
status: backlog
priority: low
created: 2026-11-05
---

## Description

`actor()` in `src/chitty/actor.py` raises `cannot determine actor` outside an agent session, so `chitty edit TASK-142 -s doing` failed when the human ran it on 2026-11-05. Decide what a person's actor should be before this is refined. A fallback must not credit an unsupported agent's writes to a person.

## History

- 2026-11-05T09:37:44Z mellow-newt → backlog
