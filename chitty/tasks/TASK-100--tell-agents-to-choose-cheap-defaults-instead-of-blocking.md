---
title: Tell agents to choose cheap defaults instead of blocking
status: done
priority: high
created: 2026-11-02
---

## Description

An agent blocked `TASK-55` and filed `HUMAN-8` for a scope question with an obvious, easily changed answer. The human decided (2026-11-02): when a decision has a sensible default that is cheap to change later, agents choose it and carry on, call it out in the ticket notes for the reviewer, and comment the code saying how and why the default was chosen. Block or file a human ticket only when the choice is costly to reverse.

## Acceptance Criteria

- [x] The managed guide (`src/chitty/guide.md`) says this, and the repo `AGENTS.md` is refreshed
- [x] The Pi work and continuation prompts say this; a Node test fails without it
- [x] `__version__` is bumped so other repos pick up the guide

## Plan

1. Add a failing Node test for the work and continuation prompts. 2. Add the rule to `src/chitty/guide.md` beside the blocking rule and to both Pi work prompts. 3. Bump `__version__` to 0.1.14, run `chitty init` to refresh `AGENTS.md` and the Pi extension, run `make check` and the Node tests.

## Notes

Version bumped to 0.1.14, so HUMAN-4 can release 0.1.14 without another bump. Running Pi loops need a restart to load the new prompt.

Reviewed: verified the refreshed managed guide and repository `AGENTS.md`, both Pi work prompts, the `0.1.14` version bump, and the Node regression test. `npm test`, `make check`, and `chitty check` pass (the latter reports only existing archived-ticket warnings).

## History

- 2026-11-02 → todo
- 2026-11-02 todo → doing
- 2026-11-02 doing → review
- 2026-11-02 review → done
