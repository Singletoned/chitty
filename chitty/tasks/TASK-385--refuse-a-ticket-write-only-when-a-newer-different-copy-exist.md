---
title: Refuse a ticket write only when a newer, different copy exists elsewhere
status: planning
depends_on:
  - TASK-378
  - TASK-382
  - TASK-383
  - TASK-384
  - TASK-393
  - TASK-522
  - TASK-537
  - TASK-547
parent: TASK-376
created: 2026-11-18
---

## Description

Replanned 2026-11-23 as part (2) of the 2026-11-22 split (see Notes): wire the settled write rule into the existing guard. Removing `Edit.skip_current_version` and `allow_stale`, and the remote-only review handoff, are TASK-647; moving `_prepare_write` after the guard is TASK-648.

Today every ticket write runs `Repo._require_current_version` in `src/chitty/store.py`. It refuses whenever the ticket's chosen source (`StoredTask.branch`) is another branch, with one exception for a ticket's own fresh worktree, and words the refusal itself (`<ID>'s latest committed version is on branch <b>; ...`). That refuses writes that would lose nothing, for example editing a ticket from a `feature` worktree whose copy is identical to `main`'s.

Owner decisions, 2026-11-22: a write is refused only when another copy of the ticket differs from the one this checkout would write over and is newer, so the write would be lost or hidden; identical copies never block a write. When refused, Chitty refuses (it does not write elsewhere), and the message is `write_refusal` (`src/chitty/write_guard.py`, TASK-547).

Change, in `src/chitty/store.py`:

- Rename `_require_current_version` to `_require_writable` and keep every call site and the `skip_current_version` / `allow_stale` bypasses as they are.
- Its rule: when `stored.branch is None` (the working tree is the source) or `stored.branch == self._current_branch()` (kept from today's guard; `ticket_source` normally returns the working tree then), allow. Otherwise read the ticket's files on `stored.branch` (`self._ref_ticket_files(<full ref>, stored.id)`, the full ref as defined below; use `stored.branch`, not a fresh source choice, so a `StoredTask` built by a test is honoured) and in this checkout's working tree (`self._working_ticket_files(stored.id)`); allow when the two lists are equal (same relative paths, same text), else refuse. "Newer" needs no separate test: the chosen source is by construction the copy Chitty reads, so a differing working-tree copy is the one that would be lost or would hide it.
- This replaces the own-worktree exception (`changed_since_split`): a fresh ticket worktree whose copy still equals `main`'s is allowed by equality, and one where `main` changed the ticket since the split is refused, as today.
- Refuse with `ChittyError(write_refusal(...))`, with arguments: `task_id=str(stored.id)`; `newer_ref=stored.branch`; `newer_sha` from `git.ref_commit(self.root, <full ref>)`, the full ref being `refs/heads/<branch>` when `git.has_local_branch(self.root, branch)` (this includes `main`) and `refs/remotes/<branch>` otherwise; `main_branch=self._main_branch()`; `local_branch=git.has_local_branch(self.root, branch)`; `worktree=git.worktree_for_branch(self.root, branch)` when local, else `None`; `main_checkout=git.main_checkout(self.root)`; `checkout_is_main` true when `self.root.resolve() == main_checkout.resolve()`; `local_behind` true when the branch is remote-tracking and `git.has_local_branch(self.root, <part after the first />)`. Take `local_branch` from `git.has_local_branch`, not from the name, since a local branch name may contain `/`.
- If `git.ref_commit` returns `None` for the full ref, raise `ChittyError(f"{stored.id}: ref {full_ref} has no commit")`; do not pass `None` on.
- Decided: the comparison is of raw text, byte for byte, not parsed tickets. A copy that differs from the one Chitty reads is refused even when this checkout's copy is the later one (for example a `feature` branch that committed a ticket change `main` lacks): that is today's behaviour, and the message keeps `write_refusal`'s wording (`has a newer copy on`), which TASK-547 settled.
- Decided: an uncommitted edit in this checkout to a ticket read from another ref makes the lists differ, so the write is refused with the same message. Writing would replace that uncommitted text with the other ref's copy plus the change, so the refusal is right even though the other copy is not newer in time; the matrix's uncommitted-edit variants cover it.
- Read errors before the guard keep their own messages (`diverged refs`, `changed on both`, `no task`).

Out of scope: TASK-647, TASK-648, multi-ticket writes (TASK-397) and docs (TASK-387).

Property tool: Hypothesis is not needed; the input space is the fixed placement matrix in `tests/ticket_placements.py` (placements `a` to `m`, checkout kinds 2 to 5, plus the main checkout), which this ticket enumerates fully.

Tests, in a new `tests/test_ticket_placement_writes.py`, reusing `make_repo`, `place`, `checkout` and `edit_uncommitted` from `tests/ticket_placements.py`, and collecting mismatches into a list asserted empty, as `tests/test_ticket_placement_reads.py` does. For each checkout (the main checkout, and kinds 2 to 5), each placement, and each uncommitted-edit variant that file already uses for that checkout, the expected read is what `tests/test_ticket_placement_reads.py` expects there (`placement_mismatches` for the main checkout, `own_worktree_mismatches` rows for kind 2, `test_linked_worktree_placements` for kinds 3 to 5). Then call `Repo.open(<checkout>).edit(TaskId("TASK", 5), Edit(note="x"))` in-process, as the read tests call `find`:

- expected read error or no ticket: raises `ChittyError` containing that read error's text;
- otherwise, writable exactly when the checkout's working tree holds exactly one `TASK-5` file and its `(title, archived)` (parsed from disk in the test, not through `Repo`) equals the expected read's `(title, archived)`. The fixture writes every copy from one template, so equal titles mean equal text.
- A writable edit returns and the file gains the note. A refused edit raises `ChittyError` whose message starts `TASK-5 has a newer copy on <ref> (`, where `<ref>` is `task-5` for placements `b`, `d` and `g` (in `d` the local branch and `origin/task-5` share a tip, so the local one is chosen), `origin/task-5` for `c` and `l`, and `main` where the expected source is `main`; it changes no file under `chitty/` in that checkout and leaves `HEAD` unchanged.

Examples with the full message, in the same file: in the main checkout, placement `b` gives `TASK-5 has a newer copy on task-5 (<sha10>); run git switch task-5 first`, placement `c` gives `...; run git switch --track origin/task-5 first`, placement `l` gives `TASK-5 has a newer copy on origin/task-5 (<sha10>); fast-forward task-5 to origin/task-5 first`; from a kind 4 worktree, placement `b` with a worktree added for `task-5` gives `...; edit it in worktree <path>`; in the main checkout switched by `git checkout -b feature main^` after placement `j` (so `main` holds `main-2` and the checkout holds `branch`), `...; switch this checkout to main first`; from a kind 4 worktree reset with `git reset --hard main^` after placement `j`, `...; edit it in the main checkout <main checkout path>`. `<sha10>` is the first 10 characters of `git rev-parse <full ref>`.

Three more examples, because the fixture's copies differ only in title: from a kind 4 worktree after placement `a`, (1) replace only the `Fixture.` body line of the working-tree file with `Changed.` (title unchanged), and (2) move the working-tree file into `chitty/tasks/archive/` without changing its text; each edit is refused with a message starting `TASK-5 has a newer copy on main (` and leaves the file as it was. (3) append one trailing newline to the working-tree file, changing nothing else; refused the same way. They fail for an implementation that compares only titles, only paths, or parsed or whitespace-normalised text.

The tests use `tests/support.py`'s `CONFIG`, which has `autocommit = false`, so `_prepare_write` (TASK-648) commits nothing in these tests.

Existing tests that assert the old guard, and what each becomes:

Checked 2026-11-23 by running each against a prototype of the rule (the equality check above, with a shortened message):

- `tests/test_own_worktree_writes.py`: `test_cli_write_then_refuse_after_merge_and_main_change` and `test_guard_refuses_changed_main` stay refusals; assert `TASK-6 has a newer copy on main (` instead of the old text. `test_guard_refuses_other_source` stays a refusal (the `feature` copy differs from the worktree's); assert `TASK-6 has a newer copy on feature (`. `test_guard_allows_unchanged_main` calls `_require_writable`. `test_guard_refuses_other_checkout` sets up a copy identical to `main`'s, which the new rule allows: rename it `test_guard_allows_identical_other_checkout` and assert no error.
- `tests/test_edit_human.py`: `test_edit_without_human_still_refuses` and `test_human_edit_without_a_worktree_keeps_the_refusal` stay refusals; assert `TASK-1 has a newer copy on task-1 (` and `TASK-3 has a newer copy on task-3 (` with `run git switch task-3 first` (no backticks, as `write_refusal` words it).
- `tests/test_check_cross_branch_references.py` `test_edit_on_another_branch_is_refused`: the copies are identical, so the edit now succeeds. Rename it `test_edit_on_another_branch_with_identical_copy_is_written` and assert exit 0 and that `chitty/tasks/TASK-1--one.md` on branch `b` now names `TASK-2`.
- `tests/test_provisional_ids.py` `test_move_provisional_off_main_then_promote_on_main`: the `move TASK-1 human` step from the worktree now succeeds for the same reason. Drop the refusal assertion and assert the move's exit 0 instead; keep the rest of the test.
- `tests/test_cli.py` `TestCrossBranchWrites` assert substrings (`git switch task-1`, `git switch --track origin/task-1`, the worktree path) that `write_refusal`'s messages contain, so they should pass unchanged; fix any that do not to the new message.

## Acceptance Criteria

- [ ] In the placement matrix in `tests/test_ticket_placement_writes.py`, every edit the oracle calls writable succeeds and adds the note, and every expected read error is raised unchanged. Before the change it fails (placement `a` from a kind 4 worktree is refused today); record that run in a note
- [ ] In the same matrix, every refused edit raises with `TASK-5 has a newer copy on <ref> (` for the stated `<ref>`, and changes no file under `chitty/` in that checkout and not `HEAD`
- [ ] The six full-message examples and the three body-only, path-only and whitespace-only examples in the same file pass
- [ ] `git grep -n _require_current_version -- src tests` prints nothing; the existing tests listed in the Description are updated as stated; `make check` passes

## Notes

Returned to planning 2026-11-20: the write rule changed (see the Description). Criterion 1 still says writes succeed exactly where the ticket is read from the working tree; that is now wrong for a ticket edited in its own fresh branch worktree.

Split plan 2026-11-22 (overnight planner), since every dependency is now done but the ticket is too large for the worker model: (1) `TASK-547`, the pure message function; (2) this ticket, narrowed to wiring `_require_writable` into the write paths using `write_refusal`, tested over the landed placement matrix (`tests/ticket_placements.py`, kinds 1 to 5) with a mismatch collector as in `tests/test_ticket_placement_reads.py`; (3) a new ticket removing `skip_current_version`/`allow_stale` and the remote-only review handoff (old criteria 2 and 3); (4) a new ticket moving `_prepare_write` after the guard (old criterion 4). Replan (2) after `TASK-547` lands.

Parked with `TASK-547`: see the question in `TASK-547`'s last note.

Owner answer, 2026-11-22: "a write is allowed only when the ticket is read from this checkout's own files" is a misinterpretation; where the ticket is read from does not matter, particularly when all branches hold the same text. Settled rule (as on 2026-11-20): a write is refused only when another copy of the ticket differs from the one this checkout would write over and is newer, so the write would be lost or hidden. When every copy is identical, the write is allowed anywhere. The five refusal messages in the Decisions above, and `TASK-547`'s rules 1 and 2, are superseded.

Open question for the owner: when a newer, different copy exists elsewhere (typically the ticket is in flight on `task-<n>`), should Chitty (A) refuse, saying where the newer copy is and where to edit it (for example `TASK-5 has a newer copy on task-5 (abc1234); edit it in worktree .worktrees/task-5`), or (B) apply the edit to that copy itself: write the file in the branch's worktree and commit there (and refuse only when the branch has no worktree, or that worktree has uncommitted changes to the ticket)?

Owner decision, 2026-11-22: (A) refuse when a newer, different copy exists elsewhere, naming that copy and where to edit (`TASK-547` words the message). Replan this ticket after `TASK-547` lands: the condition is "the authoritative copy (`stored.branch is not None`) differs from this checkout's working-tree copy", not "read from elsewhere".

Planner, 2026-11-22 (from `TASK-547`'s cold read): the replan must supply `newer_sha`. `StoredTask` (`src/chitty/store.py` around line 103) and `SourceCopy` carry no commit; `_choose_source` has the tips from `_branch_tips()` but drops them. Decide between adding a `sha` field filled from that tip map, or calling `git.ref_commit` on the ref at the guard. Take `local_branch` from `git.has_local_branch`, since a local branch name may contain `/`.

Planner, 2026-11-23: replanned as part (2). The checkout kinds are the main checkout and kinds 2 to 5 of `tests/ticket_placements.py` (there is no kind 1 there; the split plan above says 1 to 5 loosely). Split-off parts are TASK-647 (remove the bypass, remote-only review handoff) and TASK-648 (`_prepare_write` after the guard). A prototype of the rule (equality of `_source_files` and `_working_ticket_files` lists) run over placements `a`–`m` in kinds 3 to 5 agreed with the oracle; today, placements `a` and `j` from a kind 4 worktree are refused with `latest committed version is on branch main`.

## History

- 2026-11-18T16:20:16Z lively-quartz-crane → backlog
- 2026-11-18T16:23:23Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:35:59Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:35:59Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:34Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:53:38Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:53:38Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:56:14Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:59:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:59:08Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:59:12Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:01:35Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:01:35Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:01:37Z lively-quartz-crane planning → todo
- 2026-11-20T11:15:18Z lively-bronze-crane: changed description, notes
- 2026-11-20T11:15:18Z lively-bronze-crane todo → planning
- 2026-11-21T23:06:25Z lively-zinc-newt: changed dependencies
- 2026-11-22T00:19:39Z lively-zinc-newt: changed dependencies
- 2026-11-22T02:28:48Z lively-zinc-newt: changed dependencies, notes
- 2026-11-22T02:30:04Z lively-zinc-newt: changed labels, notes
- 2026-11-22T11:15:41Z friendly-jade-stoat: changed notes
- 2026-11-22T11:24:46Z friendly-jade-stoat: changed labels, notes
- 2026-11-22T11:25:47Z friendly-jade-stoat: changed notes
- 2026-11-23T14:37:10Z youthful-quartz-zander: changed title, description, acceptance criteria
- 2026-11-23T14:37:16Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:38:40Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:38:45Z youthful-quartz-zander: changed description
- 2026-11-23T14:38:49Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:40:32Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:40:40Z youthful-quartz-zander: changed description, acceptance criteria, notes
- 2026-11-23T14:40:53Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:42:40Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:42:49Z youthful-quartz-zander: changed description, acceptance criteria
- 2026-11-23T14:43:04Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:44:41Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:44:45Z youthful-quartz-zander: changed description
- 2026-11-23T14:44:56Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:46:28Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:46:33Z youthful-quartz-zander: changed description, acceptance criteria
