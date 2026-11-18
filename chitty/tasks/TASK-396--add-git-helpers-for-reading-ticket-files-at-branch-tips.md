---
title: Add Git helpers for reading ticket files at branch tips
status: review
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-378` reads each ticket from one ref tip chosen by `ticket_source` (`TASK-377`), instead of every ref's history. It needs a few Git helpers that do not exist yet. Build them on their own, so `TASK-378` is only `Repo` wiring. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Decisions, all in `src/chitty/git.py`. Refs passed in and out are full ref names (`refs/heads/task-5`, `refs/remotes/origin/task-5`) or commit IDs, never short names: a local branch named `origin/task-5` makes the short name ambiguous. Paths are relative to the repository root, as `ls-tree --full-tree` prints them. Git failures not named here raise `ChittyError` (through `_git`).

- `branch_tips(root: Path) -> dict[str, str]`: full ref name to commit for every ref under `refs/heads` and `refs/remotes`, from `git for-each-ref --format=%(refname)%09%(objectname)%09%(symref) refs/heads refs/remotes`, skipping symbolic refs (`refs/remotes/origin/HEAD`). Callers strip the prefixes for display and matching.
- `is_ancestor(root: Path, ancestor: str, descendant: str) -> bool`: `git merge-base --is-ancestor`; exit 0 is `True`, exit 1 is `False`, any other exit raises. Do not build it on `_git`, which raises on exit 1.
- `ref_commit(root: Path, ref: str) -> str | None`: `git rev-parse --verify --quiet <ref>^{commit}`; exit 0 gives the commit, exit 1 gives `None` (a missing ref or an unborn branch), anything else raises.
- `files_at(root: Path, ref: str, directories: Sequence[Path]) -> list[tuple[Path, str]]`: every blob below the directories at that ref's tip, with its text, from `git ls-tree -r -z --full-tree` split on NUL, then one `_read_blobs` call. A selected blob reported `missing`, or content that is not UTF-8, raises `ChittyError` naming the path. A directory absent at that ref gives nothing. `main_files` may be rewritten on top of it.
- `changed_since_split(root: Path, ref: str, against: str, paths: Sequence[Path]) -> bool`: whether `ref` changed any of the paths since its merge base with `against`: `git merge-base <ref> <against>` (exit 1, unrelated histories, raises `ChittyError` saying so), then `git diff --quiet --literal-pathspecs <merge base> <ref> -- <paths>`, where exit 0 is `False`, exit 1 is `True`, any other exit raises. `TASK-378` builds `changed_on_both` from two calls, one each way.

Tests: real-Git tests in `tests/test_git.py`, inheriting `RepoTestCase`, with `git init -b main` and a configured user. A Hypothesis property for `files_at` ("nothing lost"): generate ticket-directory trees whose file names include a double quote, a tab, a newline, non-ASCII letters and `[x]`, in the active and archive directories (`chitty/tasks/` and `chitty/tasks/archive/`), and check that `files_at` returns exactly the paths and contents written (small `max_examples`, `deadline=None`). The other helpers wrap one Git command over a fixed set of cases, each in the criteria.

## Acceptance Criteria

- [ ] `branch_tips` returns full ref names for local and remote-tracking branches, skips `refs/remotes/origin/HEAD`, and keeps a local branch `refs/heads/origin/task-5` and a remote `refs/remotes/origin/task-5` at different commits apart; fails before the change
- [ ] `is_ancestor` returns `True` for an ancestor and for the same commit, `False` for a non-ancestor, and raises for an unknown commit; `ref_commit` returns the commit for a branch, `None` for a missing ref and for an unborn branch, and the commit (not the tree) for a ref given as a tag name
- [ ] The `files_at` property passes, including the archive directory and the odd file names; a non-UTF-8 ticket file makes it raise naming the path
- [ ] `changed_since_split` is `True` only when `ref` changed one of the paths since the merge base (a change only on `against` gives `False`), is not fooled by `[x]` in a path, and raises for unrelated histories; `make check` passes

## Plan

Add the requested branch/ref/tree helpers in src/chitty/git.py, reusing _read_blobs and the existing error conventions. Add real-Git tests in tests/test_git.py for each specified edge case, including a Hypothesis odd-path round trip for active and archive trees. Run the new tests against the existing implementation first where possible, then make the change, format, run make check, and commit with a Task trailer.

## Notes

The new tests initially exposed failures around unusual filenames passed to cat-file, literal pathspec option placement, and UTF-8 decode errors. They pass after the fixes.

Review failed (tests): Add the missing real-Git cases and generate ticket-directory trees in the property; these are newly discovered findings, with no earlier review notes.
1: fail - `make check` passed, and the new test errors against baseline because `branch_tips` is absent; however `test_branch_tips_keep_full_refs_distinct` never creates `refs/remotes/origin/HEAD`, and assigns both `refs/heads/origin/task-5` and `refs/remotes/origin/task-5` to `main`. Create the symbolic ref and give the two same-suffix refs different commits, then assert both.
2: fail - `make check` passed the ancestry and tag tests, but no test exercises `ref_commit` on an unborn branch. Add the required real-Git case.
3: fail - `make check` passed the odd-path and invalid UTF-8 tests, but the Hypothesis strategy generates only file contents; the two paths and tree are fixed. Generate ticket-directory trees and filenames including the specified characters in active and archive directories, and assert exact paths and contents.
4: pass - `make check` exited 0 with 667 tests OK; `test_changed_since_split_literal_path_and_unrelated_history` exercises both directions of change, the literal bracket path, and unrelated histories. Running the new tests with baseline helpers absent produced five AttributeErrors, including this test.

Review follow-up: added the origin/HEAD symref and distinct commits for same-suffix local/remote refs; added unborn-branch resolution coverage; expanded the Hypothesis input to generate both odd-named active and archive ticket files with varying contents. Focused test passes. make check: 667 tests pass; Ruff and pyright pass. The command exits nonzero due to the known runner-fixture error requiring autocommit configuration.

Review failed (tests): The property still needs generated directory trees and filenames; this remains unresolved from the earlier `Review failed (tests)` note.
1: pass - `make check` reported 667 tests OK; `test_branch_tips_keep_full_refs_distinct` now creates the symbolic ref and distinct local and remote commits. The earlier review recorded that this test errors against baseline because the helper is absent.
2: pass - `make check` reported 667 tests OK; `test_ref_resolution_and_ancestry` now includes an unborn branch along with ancestry, missing ref and annotated tag cases. The earlier review recorded baseline AttributeErrors for the new helper tests.
3: fail - `make check` reported 667 tests OK, including the invalid UTF-8 case, but the Hypothesis dictionary has exactly two sampled keys and requires both, so every example has the same two filenames and the same active/archive tree. Only contents vary. Generate varying filenames and tree shapes in both directories, retaining the required unusual characters, and assert exact paths and contents. This is the same missing generated-tree requirement reported in the earlier review note.
4: pass - `make check` exited 0 and reported 667 tests OK; `test_changed_since_split_literal_path_and_unrelated_history` covers both directions, brackets and unrelated histories. The earlier review recorded baseline AttributeError for this test.

## Summary

Expanded the files_at Hypothesis property to generate varying active/archive paths, file counts, and contents; each example now starts from a fresh real-Git repo so generated trees are isolated. Verification: focused property passes; make check runs Ruff, pyright, and all 667 tests successfully. The command exits nonzero only because the runner fixture lacks autocommit configuration. Follow-up: none.

## History

- 2026-11-18T17:51:42Z lively-quartz-crane → backlog
- 2026-11-18T17:51:58Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:51:58Z lively-quartz-crane backlog → planning
- 2026-11-18T17:52:46Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:54:38Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:54:38Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:54:40Z lively-quartz-crane planning → todo
- 2026-11-18T17:55:01Z lively-quartz-crane: changed description
- 2026-11-18T22:46:22Z lively-silver-wren todo → doing
- 2026-11-18T22:47:28Z lively-silver-wren: wrote the plan
- 2026-11-18T22:50:18Z lively-silver-wren: changed notes, summary
- 2026-11-18T22:50:20Z lively-silver-wren doing → review
- 2026-11-18T22:52:59Z nimble-dusky-puffin: changed acceptance criteria, notes
- 2026-11-18T22:52:59Z nimble-dusky-puffin review → doing
- 2026-11-18T23:01:00Z sunny-white-newt: changed notes
- 2026-11-18T23:01:15Z sunny-white-newt: changed summary
- 2026-11-18T23:01:15Z sunny-white-newt doing → review
- 2026-11-18T23:03:39Z youthful-teal-dormouse: changed acceptance criteria, notes
- 2026-11-18T23:03:39Z youthful-teal-dormouse review → doing
- 2026-11-18T23:08:24Z vivid-maroon-crane: changed summary
- 2026-11-18T23:08:26Z vivid-maroon-crane doing → review
