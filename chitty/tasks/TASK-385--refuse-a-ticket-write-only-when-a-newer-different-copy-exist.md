---
title: Refuse a ticket write only when a newer, different copy exists elsewhere
status: cold-read
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
- Its rule: when `stored.branch is None` (the working tree is the source), allow. Otherwise read the ticket's raw files at the source (`self._source_files(stored.id)`, the `(path, text)` list already used for reading) and in this checkout's working tree (`self._working_ticket_files(stored.id)`); allow when the two lists are equal (same relative paths, same text), else refuse. "Newer" needs no separate test: the chosen source is by construction the copy Chitty reads, so a differing working-tree copy is the one that would be lost or would hide it.
- This replaces the own-worktree exception (`changed_since_split`): a fresh ticket worktree whose copy still equals `main`'s is allowed by equality, and one where `main` changed the ticket since the split is refused, as today.
- Refuse with `ChittyError(write_refusal(...))`, with arguments: `task_id=str(stored.id)`; `newer_ref=stored.branch`; `newer_sha` from `git.ref_commit(self.root, <full ref>)`, the full ref being `refs/heads/<branch>` when `git.has_local_branch(self.root, branch)` (this includes `main`) and `refs/remotes/<branch>` otherwise; `main_branch=self._main_branch()`; `local_branch=git.has_local_branch(self.root, branch)`; `worktree=git.worktree_for_branch(self.root, branch)` when local, else `None`; `main_checkout=git.main_checkout(self.root)`; `checkout_is_main` true when `self.root.resolve() == main_checkout.resolve()`; `local_behind` true when the branch is remote-tracking and `git.has_local_branch(self.root, <part after the first />)`. Take `local_branch` from `git.has_local_branch`, not from the name, since a local branch name may contain `/`.
- Read errors before the guard keep their own messages (`diverged refs`, `changed on both`, `no task`).

Out of scope: TASK-647, TASK-648, multi-ticket writes (TASK-397) and docs (TASK-387).

Property tool: Hypothesis is not needed; the input space is the fixed placement matrix in `tests/ticket_placements.py` (placements `a` to `m`, checkout kinds 2 to 5, plus the main checkout), which this ticket enumerates fully.

Tests, in a new `tests/test_ticket_placement_writes.py`, reusing `make_repo`, `place`, `checkout` and `edit_uncommitted` from `tests/ticket_placements.py`, and collecting mismatches into a list asserted empty, as `tests/test_ticket_placement_reads.py` does. For each checkout (the main checkout, and kinds 2 to 5), each placement, and each uncommitted-edit variant that file already uses for that checkout, the expected read is what `tests/test_ticket_placement_reads.py` expects there (`placement_mismatches` for the main checkout, `own_worktree_mismatches` rows for kind 2, `test_linked_worktree_placements` for kinds 3 to 5). Then call `Repo.open(<checkout>).edit(TaskId("TASK", 5), Edit(note="x"))` in-process, as the read tests call `find`:

- expected read error or no ticket: raises `ChittyError` containing that read error's text;
- otherwise, writable exactly when the checkout's working tree holds exactly one `TASK-5` file and its `(title, archived)` (parsed from disk in the test, not through `Repo`) equals the expected read's `(title, archived)`. The fixture writes every copy from one template, so equal titles mean equal text.
- A writable edit returns and the file gains the note. A refused edit raises `ChittyError` whose message starts `TASK-5 has a newer copy on <ref> (`, where `<ref>` is `task-5` for placements `b`, `d` and `g` (in `d` the local branch and `origin/task-5` share a tip, so the local one is chosen), `origin/task-5` for `c` and `l`, and `main` where the expected source is `main`; it changes no file under `chitty/` in that checkout and leaves `HEAD` unchanged.

Examples with the full message, in the same file: in the main checkout, placement `b` gives `TASK-5 has a newer copy on task-5 (<sha10>); run git switch task-5 first`, placement `c` gives `...; run git switch --track origin/task-5 first`, placement `l` gives `TASK-5 has a newer copy on origin/task-5 (<sha10>); fast-forward task-5 to origin/task-5 first`; from a kind 4 worktree, placement `b` with a worktree added for `task-5` gives `...; edit it in worktree <path>`; in the main checkout switched by `git checkout -b feature main^` after placement `j` (so `main` holds `main-2` and the checkout holds `branch`), `...; switch this checkout to main first`; from a kind 4 worktree reset with `git reset --hard main^` after placement `j`, `...; edit it in the main checkout <main checkout path>`. `<sha10>` is the first 10 characters of `git rev-parse <full ref>`.

## Acceptance Criteria

- [ ] The placement matrix in `tests/test_ticket_placement_writes.py` passes: every writable edit succeeds and adds the note, every refused edit raises with `TASK-5 has a newer copy on <ref> (` for the stated `<ref>` and changes no file under `chitty/` or `HEAD`, and every read error is unchanged. Before the change it fails (for example placement `a` from a kind 4 worktree is refused today); record that run in a note
- [ ] The six full-message examples in the same file pass
- [ ] `git grep -n _require_current_version -- src tests` prints nothing; `make check` passes

## Notes

Returned to planning 2026-11-20: the write rule changed (see the Description). Criterion 1 still says writes succeed exactly where the ticket is read from the working tree; that is now wrong for a ticket edited in its own fresh branch worktree.

Split plan 2026-11-22 (overnight planner), since every dependency is now done but the ticket is too large for the worker model: (1) `TASK-547`, the pure message function; (2) this ticket, narrowed to wiring `_require_writable` into the write paths using `write_refusal`, tested over the landed placement matrix (`tests/ticket_placements.py`, kinds 1 to 5) with a mismatch collector as in `tests/test_ticket_placement_reads.py`; (3) a new ticket removing `skip_current_version`/`allow_stale` and the remote-only review handoff (old criteria 2 and 3); (4) a new ticket moving `_prepare_write` after the guard (old criterion 4). Replan (2) after `TASK-547` lands.

Parked with `TASK-547`: see the question in `TASK-547`'s last note.

Owner answer, 2026-11-22: "a write is allowed only when the ticket is read from this checkout's own files" is a misinterpretation; where the ticket is read from does not matter, particularly when all branches hold the same text. Settled rule (as on 2026-11-20): a write is refused only when another copy of the ticket differs from the one this checkout would write over and is newer, so the write would be lost or hidden. When every copy is identical, the write is allowed anywhere. The five refusal messages in the Decisions above, and `TASK-547`'s rules 1 and 2, are superseded.

Open question for the owner: when a newer, different copy exists elsewhere (typically the ticket is in flight on `task-<n>`), should Chitty (A) refuse, saying where the newer copy is and where to edit it (for example `TASK-5 has a newer copy on task-5 (abc1234); edit it in worktree .worktrees/task-5`), or (B) apply the edit to that copy itself: write the file in the branch's worktree and commit there (and refuse only when the branch has no worktree, or that worktree has uncommitted changes to the ticket)?

Owner decision, 2026-11-22: (A) refuse when a newer, different copy exists elsewhere, naming that copy and where to edit (`TASK-547` words the message). Replan this ticket after `TASK-547` lands: the condition is "the authoritative copy (`stored.branch is not None`) differs from this checkout's working-tree copy", not "read from elsewhere".

Planner, 2026-11-22 (from `TASK-547`'s cold read): the replan must supply `newer_sha`. `StoredTask` (`src/chitty/store.py` around line 103) and `SourceCopy` carry no commit; `_choose_source` has the tips from `_branch_tips()` but drops them. Decide between adding a `sha` field filled from that tip map, or calling `git.ref_commit` on the ref at the guard. Take `local_branch` from `git.has_local_branch`, since a local branch name may contain `/`.

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
