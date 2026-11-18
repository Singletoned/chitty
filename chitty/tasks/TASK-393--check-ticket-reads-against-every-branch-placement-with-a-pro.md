---
title: Check ticket reads against every branch placement with a property
status: planning
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-378` makes `Repo` read each ticket from the place `ticket_source` names and tests a fixed list of placements. Bugs in the wiring (wrong inputs to `ticket_source`, swapped `contains` arguments, a missed directory) can hide between fixed cases. Add a generated property over placements. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` lands.

Decisions:

- New `tests/test_property_ticket_reads.py`, inheriting `RepoTestCase` from `tests/support.py`. Each example builds a fresh repository in its own subdirectory (`tempfile.mkdtemp(dir=self.tmp)`). Settings: `deadline=None`, `max_examples` about 20, `derandomize=True`, `database=None`; pin `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` on every commit, drawn at random so commit order differs from causal order.
- Generate 1 to 4 tickets, each with a placement drawn by `st.sampled_from` over: only on `main`; on `main` and edited on its local branch; on `main` and edited only on `origin/<branch>` (`git update-ref refs/remotes/origin/<branch> <commit>`); local branch behind `origin/<branch>`; local and remote diverged; only on an unrelated branch; also on decoy branches (`task-50` for `TASK-5`, `feature/task-5`). Generate the reading checkout: the main checkout, one ticket's linked worktree, or a checkout of an unrelated branch. Record each placement with `hypothesis.event` so the run shows every one was drawn.
- The expected result comes from the placement the test built, not from calling `ticket_source`: main-only gives `main`'s content; a local edit with no remote, or with the remote behind, gives the local content; a remote ahead gives the remote content; diverged raises naming both; unrelated-only is not listed; in the ticket's own worktree, the working-tree content; decoys never change the result.

No production code changes unless the property finds a bug; then fix it here, with the failing example kept as an explicit test.

## Acceptance Criteria

- [ ] The property passes over generated placements and checkouts, comparing `Repo.find` and `Repo.tasks` against the placement-derived expectation, and `hypothesis.event` output shows every placement drawn at least once in a run
- [ ] Mutation evidence: swapping the arguments of the `contains` callback passed to `ticket_source`, or passing `main_branch` as `current_branch`, makes the property fail (shown by running it against each change, then reverting); `make check` passes

## History

- 2026-11-18T16:38:03Z lively-quartz-crane → backlog
- 2026-11-18T16:39:33Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:33Z lively-quartz-crane backlog → planning
