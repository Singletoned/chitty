---
title: Stop telling agents to escape literal asterisks
status: doing
depends_on:
  - TASK-530
parent: TASK-348
created: 2026-11-21
---

## Description

Split from `TASK-348` on 2026-11-21. Once `TASK-529` and `TASK-530` make Chitty escape lone literal asterisks itself, the guides no longer need to tell agents to do it.

Remove the instruction, which today reads `When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.` (wrapped differently in each file):

- `src/chitty/guide.md` (line 4): delete only that sentence; keep `Put paths, commands, IDs, and code in backticks.`
- `src/chitty/roles/work.md` (line 8) and `src/chitty/roles/review.md` (line 6): delete the bullet that holds it.
- `src/chitty/roles/plan.md` (lines 12-14): the sentence is the second half of the bullet that starts `Put paths, globs, commands, IDs, and code in backticks`; delete only the sentence and keep the first half.
- `tests/fixtures/guide-runner-expected.md` (line 4) holds the managed guide text and is compared exactly by `tests/test_guide_workflow_block.py`: remove the same sentence there.
- Delete `tests/test_guide_literal_star.py`, the test that asserts the sentence is present. Do not replace it.

Out of scope: `AGENTS.md` (its hand-written `## Chitty` section also has the sentence, near line 57). After this lands, the main checkout's `chitty init` refreshes the managed block, and the planning session removes the hand-written copy.

## Acceptance Criteria

- [ ] `git grep -n -e "literal single" -e "escape it or enclose" -- src/chitty tests` finds nothing, the first half of the `plan.md` bullet and the backticks sentence in `guide.md` remain, and `tests/test_guide_literal_star.py` is gone; `make check` passes

## History

- 2026-11-21T23:22:21Z lively-zinc-newt → todo
- 2026-11-21T23:22:30Z lively-zinc-newt todo → cold-read
- 2026-11-21T23:23:20Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:23:20Z lively-zinc-newt cold-read → todo
- 2026-11-22T01:47:26Z zesty-yellow-jay todo → doing
