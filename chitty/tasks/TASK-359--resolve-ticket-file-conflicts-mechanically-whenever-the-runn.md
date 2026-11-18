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

Why taking one whole side is safe: every Chitty write starts from the newest committed version (`Repo._require_current_version` in `src/chitty/store.py`), so the newest copy already holds every earlier copy's content. This is an assumption the ticket relies on, not something it tests; versions chosen by commit time rather than ancestry are `TASK-366`. Checked on `TASK-364`: `main`'s copy differs from the branch's only by a status, a ticked criterion, and added notes and history.

Decisions:

- `git.merge_main(root, main_branch, ticket_directories)` in `src/chitty/git.py` gains a `ticket_directories: Sequence[Path]` argument (repository-relative, no default): the active and archive directories of every configured context. When the merge stops, it reads the unmerged entries from `git status --porcelain` as `(code, path)` pairs. If `ticket_only_conflicts` accepts them, it resolves each path by taking whole the side whose newest commit touching that path is later, where the sides are `HEAD` (ours) and `MERGE_HEAD` (theirs) and the time is `git log -1 --format=%ct <side> -- <path>` with no other filtering, `HEAD` winning ties; it stages the files, commits the merge with `--no-edit`, and returns `[]`. Otherwise it aborts as today and returns every conflicting path.
- Two pure functions in `src/chitty/git.py`:
  - `newer_side(ours_committed_at: int, theirs_committed_at: int) -> Literal["ours", "theirs"]`.
  - `ticket_only_conflicts(conflicts: Sequence[tuple[str, Path]], ticket_directories: Sequence[Path]) -> bool`: true when the list is non-empty and every entry has code `UU` (both modified) and a path ending `.md` whose parent is exactly one of the directories. Any other code (for example a modify/delete after an archive move), a nested path or another file makes it false, and the merge aborts as today.
- Callers: `_prepare_review` and `_land` in `src/chitty/run.py`. `_land` switches from `git.merge` to `git.merge_main`, so landing also runs with `rerere.enabled=false`. Remove `git.merge`; its only caller moves to `merge_main`. `TASK-370` will be the third caller.
- Update step 4 of "Before a review" and the landing bullets in `docs/plan/next-action-and-runner.md`, and add the principle above.

Out of scope: picking versions by ref tip (`TASK-366`), active/archive duplicates (`TASK-367`), and the work-mode merge (`TASK-370`).

Tests:

- Hypothesis properties in a new `tests/test_property_merge_conflicts.py`. `newer_side`: for any two integer times, the result names the larger, `ours` on a tie, and swapping the arguments swaps the result except on ties. `ticket_only_conflicts`: generate directories and conflict lists mixing `UU` and other two-letter unmerged codes (`AA`, `DU`, `UD`, `AU`, `UA`, `DD`) with paths directly in a directory, nested below one, outside all, and not ending `.md`; the result is true exactly when the list is non-empty and every entry qualifies, and shuffling the list does not change it.
- Real-Git, fake-agent runner tests in `tests/test_review_merge.py`, beside `test_conflict_moves_the_ticket_to_doing_without_starting_the_agent`, and a landing test in `tests/test_landing.py`. Set `GIT_COMMITTER_DATE` on the conflicting commits so the newer side is certain (as `tests/test_store.py` does); commits in the same second tie.
- Add both functions first, raising `NotImplementedError`, so the property tests fail on behaviour rather than import.

## Acceptance Criteria

- [ ] The `newer_side` and `ticket_only_conflicts` Hypothesis properties in `tests/test_property_merge_conflicts.py` pass, and fail against the `NotImplementedError` stubs
- [ ] Review runs in `tests/test_review_merge.py` where `main` and the branch both changed only the ticket file, once with `main` later and once with the branch later, each commit the merge with the newer side's copy byte for byte, leave no merge in progress, start the reviewer, and do not hit the `latest committed version` error; the `main`-later case fails before the change
- [ ] A review run with a ticket-file conflict and a code conflict still aborts, leaves no merge in progress, and moves the ticket to `doing` with `Review failed (integration)` naming both files
- [ ] A landing in `tests/test_landing.py` whose merge of `main` conflicts only in a ticket file lands, with the newer copy on `main`; it fails before the change, and `git.merge` no longer exists
- [ ] `docs/plan/next-action-and-runner.md` states the principle and the ticket-file resolution, and `make check` passes

## History

- 2026-11-16T10:48:09Z intrepid-coral-raven → planning
- 2026-11-16T10:50:28Z intrepid-coral-raven: changed title, description
- 2026-11-18T09:13:54Z witty-ginger-falcon: changed title, description
- 2026-11-18T09:22:40Z witty-ginger-falcon: changed labels, description, acceptance criteria
- 2026-11-18T09:22:42Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:24:14Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:24:15Z witty-ginger-falcon: changed description, acceptance criteria
