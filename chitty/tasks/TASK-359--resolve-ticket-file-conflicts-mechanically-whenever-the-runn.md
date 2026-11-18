---
title: Resolve ticket-file conflicts mechanically whenever the runner merges `main`
status: planning
labels:
  - bug
created: 2026-11-16
---

## Description

Seen 2026-11-16 on `TASK-333` and 2026-11-17 on `TASK-364`. An error repair recorded a status on `main` (for example `error → review`) while the ticket branch still had its older copy of the ticket file. `_prepare_review` in `src/chitty/run.py` then merged `main`, the merge conflicted only in that ticket file, and writing the `Review failed (integration)` note from the worktree hit the stale-copy check (`TASK-364's latest committed version is on branch main`), which stopped `chitty run --loop`.

Principle (decided 2026-11-18): merging `main` into a ticket branch is mechanical and done by the runner; only code conflicts go to an agent. A ticket file is Chitty's own data, so its conflicts are mechanical too.

Why taking one whole side is safe: every Chitty write starts from the newest committed version (`Repo._require_current_version` in `src/chitty/store.py`), so the newest copy already holds every earlier copy's content. Checked on `TASK-364`: `main`'s copy differs from the branch's only by a status, a ticked criterion, and added notes and history.

Decisions:

- `git.merge_main(root, main_branch, ticket_directories)` in `src/chitty/git.py` gains a `ticket_directories: Sequence[Path]` argument (repository-relative, no default): the active and archive directories of every configured context. When the merge stops and every conflicting path (`git diff --name-only --diff-filter=U`) is a file directly in one of those directories, it resolves each path by taking whole the side whose newest commit touching that path (`git log -1 --format=%ct <side> -- <path>`) is later, with `HEAD` winning ties; it stages the files, commits the merge with `--no-edit`, and returns `[]`. Otherwise it aborts as today and returns every conflicting path.
- Put the side choice in a pure function in `src/chitty/git.py`: `newer_side(ours_committed_at: int, theirs_committed_at: int) -> Literal["ours", "theirs"]`.
- A conflict that is not a content conflict on both sides (for example modify/delete after an archive move) is not resolved: it counts as a non-ticket conflict.
- Callers: `_prepare_review` and `_land` in `src/chitty/run.py`. `_land` switches from `git.merge` to `git.merge_main`, so landing also runs with `rerere.enabled=false`. Remove `git.merge` if nothing else uses it. `TASK-370` will be the third caller.
- Update step 4 of "Before a review" and the landing bullets in `docs/plan/next-action-and-runner.md`, and add the principle above.

Out of scope: picking versions by ref tip (`TASK-366`), active/archive duplicates (`TASK-367`), and the work-mode merge (`TASK-370`).

Tests: Hypothesis property for `newer_side` in a new `tests/test_property_newer_side.py`: for any two integer times, the result names the larger, `ours` on a tie, and swapping the arguments swaps the result except on ties. Real-Git, fake-agent runner tests in `tests/test_review_merge.py`, beside `test_conflict_moves_the_ticket_to_doing_without_starting_the_agent`. Add `newer_side` first, raising `NotImplementedError`, so the property test fails on behaviour rather than import.

## Acceptance Criteria

- [ ] The `newer_side` Hypothesis property in `tests/test_property_newer_side.py` passes, and fails against the `NotImplementedError` stub
- [ ] A review run where `main` and the branch both changed only the ticket file (`main` later) commits the merge with `main`'s copy, leaves no merge in progress, starts the reviewer, and does not hit the `latest committed version` error; the same test fails before the change
- [ ] A review run where the branch changed the ticket file later than `main` keeps the branch copy
- [ ] A review run with a ticket-file conflict and a code conflict still aborts and moves the ticket to `doing` with `Review failed (integration)` naming both files; a landing whose merge conflicts only in a ticket file lands
- [ ] `docs/plan/next-action-and-runner.md` states the principle and the ticket-file resolution, and `make check` passes

## History

- 2026-11-16T10:48:09Z intrepid-coral-raven → planning
- 2026-11-16T10:50:28Z intrepid-coral-raven: changed title, description
- 2026-11-18T09:13:54Z witty-ginger-falcon: changed title, description
- 2026-11-18T09:22:40Z witty-ginger-falcon: changed labels, description, acceptance criteria
