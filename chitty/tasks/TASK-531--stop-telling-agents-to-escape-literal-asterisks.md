---
title: Stop telling agents to escape literal asterisks
status: todo
depends_on:
  - TASK-530
parent: TASK-348
created: 2026-11-21
---

## Description

Split from `TASK-348` on 2026-11-21. Once `TASK-529` and `TASK-530` make Chitty escape lone literal asterisks itself, the guides no longer need to tell agents to do it.

Remove the instruction: the sentence in `src/chitty/guide.md` and the bullets in `src/chitty/roles/work.md`, `review.md` and `plan.md` that tell agents to escape a literal single `*` or wrap it in backticks. Delete `tests/test_guide_literal_star.py`, and update `tests/fixtures/guide-before-workflow.md` only if a test fails without it. Do not change `AGENTS.md` on the branch: after this lands, the main checkout's `chitty init` refreshes its managed block, and the planning session removes the same sentence from the hand-written `## Chitty` section if it is outside the block.

## Acceptance Criteria

- [ ] No guide in `src/chitty/guide.md` or `src/chitty/roles/` tells agents to escape a literal `*`, `git grep -n "literal single"` in `src/chitty` finds nothing, and `tests/test_guide_literal_star.py` is gone; `make check` passes

## History

- 2026-11-21T23:22:21Z lively-zinc-newt → todo
