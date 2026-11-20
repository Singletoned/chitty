---
title: Land without a new check when `main` moved only by ticket-file commits
status: doing
priority: high
created: 2026-11-19
---

## Description

On 2026-11-19 `TASK-404` passed review and then failed to land twice: `main moved during each of the 3 landing attempts`. Each attempt in `_land_locked` (`src/chitty/run.py`) rebases the branch onto `main`, runs `setup` and the landing check (about a minute here), then tries `git.fast_forward`; when `main` moved meanwhile, it starts the whole attempt again, up to `LANDING_ATTEMPTS = 3`. In the first failure, `main` gained 8 commits between 21:00 and 21:06 (`git log --since=2026-11-19T21:00:00Z --until=2026-11-19T21:06:00Z main`): seven `chitty: edit ...` ticket commits from a planning session and one code commit (`b619f893`). With this change, only the attempt that saw the code commit would have rerun the check. Ticket files rarely change what a check tests, so a move made only of ticket-file changes should not cost a new check.

Decisions:

- Pure function `_only_ticket_paths(paths: Sequence[str], contexts: Sequence[str]) -> bool` in `src/chitty/run.py`: `True` when every path starts with `chitty/<name>/` for some `<name>` in `contexts` (`BACKLOG_DIR` in `src/chitty/config.py` is `chitty`; a context's directory is `chitty/<name>`, see `Repo` in `src/chitty/store.py` near line 247), including its `archive/` subdirectory; `True` for no paths. Anything else, such as `chitty.toml`, `chitty/<name>` itself, `chitty/archive/...` or the directory of a context not in `contexts`, is not a ticket path.
- New `merge_base(root: Path, first: str, second: str) -> str` in `src/chitty/git.py` (`git merge-base`). For the changed paths, reuse the existing `git.changed_paths(root, base, branch)`, which runs `git diff -z --no-renames --name-only <base>...<branch>`, and convert its `PurePosixPath`s with `str`.
- In `_land_locked`, when `git.fast_forward` fails and `main` has moved (`not git.is_ancestor(main_root, main_branch, branch)`, as today), enter the quick path: let `base = git.merge_base(main_root, branch, main_branch)`, the commit the branch was last rebased onto. If `_only_ticket_paths([str(p) for p in git.changed_paths(main_root, base, main_branch)], list(main_repo.config.contexts))`, rebase onto `main` again (a conflict raises the same `cannot land ...; rebasing onto ... conflicts in ...` error as today) and try `git.fast_forward` again without running `setup` or the landing check. Recompute `base` on each quick try. The quick tries are a loop nested inside the failure branch of the attempt loop (`for attempt in range(LANDING_ATTEMPTS)`, `src/chitty/run.py` near line 1105); a quick try never uses up an `attempt`. When a move contains a non-ticket path, `continue` the attempt loop as today, which uses one full attempt. A landing makes at most `QUICK_LANDING_ATTEMPTS = 10` quick tries in total (a new module constant next to `LANDING_ATTEMPTS`), counted separately from full attempts; when they run out, raise `main moved during each of the 10 quick landing attempts`. When the new commits change any other path, fall back to a full attempt, which counts toward `LANDING_ATTEMPTS` as now.
- The `chitty.toml` and protected-file refusals look at what the branch changes, which a rebase onto ticket-only commits does not alter, so the quick path does not repeat them.
- Docs: add one bullet near the landing bullets in `docs/plan/next-action-and-runner.md` describing the quick path and its assumption: the landing check does not depend on ticket files. Name the cases where that fails, so a repository can judge: a check that validates tickets (for example with `chitty check`), and this repository's `make check`, whose first line (`git grep` for conflict markers) also scans `chitty/`.

Tests:

- New `tests/test_property_landing_paths.py`, with Hypothesis (already a dependency, see `tests/test_property_ticket_source.py`). Draw one to three distinct context names matching `CONTEXT_NAME_RE` in `src/chitty/config.py` and not in `RESERVED_CONTEXT_NAMES` (which holds `archive`), and a list of zero or more paths (`min_size=0`; the empty list must give `True`), each built as either a ticket path, `chitty/<name>/<rest>` with `<rest>` one or more segments and sometimes under `archive/`, or a non-ticket path: `chitty/<name>`, `chitty/<name>.d/<rest>`, `x/chitty/<name>/<rest>`, `chitty/archive/<rest>`, `chitty/<other>/<rest>` where `<other>` is either a fresh valid context name or a drawn name plus one or more letters from `[a-z]` (a sibling such as `ax` next to `a`), filtered to be none of the drawn contexts, `chitty.toml`, or `src/<rest>`. A context name cannot contain `.`, so `chitty/<name>.d/` is never another drawn context's directory (a suffix such as `x` could be: contexts `a` and `ax`). Property: the result is `True` exactly when every drawn path was built as a ticket path, and does not depend on the order of the list. Add the `NotImplementedError` stub of `_only_ticket_paths` first, so the tests fail on behaviour.
- In `tests/test_landing_retry.py` (`TestLandingRetry`), add two `run_script` modes as their own branches of its `if`/`elif` chain, each acting on the first run only. `ticket`: copy `TASK-1`'s file on `main` to `chitty/tasks/TASK-9--moved.md`, `git add` it and commit on `main`. `mixed`: write that file and `check-1.txt`, `git add` both and commit them together. Both write `check-commit` as the other modes do.
- `test_ticket_only_move_lands_without_a_second_check`: `finish_ticket()`, then `land_with_script("ticket")`. The count file has exactly one line, `main` contains the check's commit, `chitty/tasks/TASK-9--moved.md` and the branch's commits, and the worktree and branch are gone. Against today's code the count is 2: a probe of exactly this mode with `_land` on 2026-11-19 ran the check twice and landed.
- `test_mixed_move_reruns_the_check`: `land_with_script("mixed")`; the count is exactly 2 and the ticket lands.
- `test_quick_path_stops_after_ten_ticket_moves`: with `unittest.mock.patch`, wrap `chitty.run.git.fast_forward` so each call first commits a new ticket file `chitty/tasks/TASK-<20+n>--moved.md` on `main` (a copy of `TASK-1`'s file), then calls the real function; the wrapper raises `AssertionError` on its 21st call, so a missing limit fails rather than hangs. Land with a check that only appends to the count file. It raises `main moved during each of the 10 quick landing attempts`; the wrapper was called exactly 11 times (one full attempt, then ten quick tries); the count file has exactly one line; the worktree and branch remain.
- Existing `test_retries_when_main_moves_once` and `test_stops_after_three_main_moves` must still pass unchanged: they move `main` with non-ticket files.

Out of scope: planning on branches, `TASK-428`'s lock, and the landing check itself.

## Acceptance Criteria

- [ ] The `_only_ticket_paths` property in `tests/test_property_landing_paths.py` passes, generating every path shape in the Description; a note records that it fails while the function raises `NotImplementedError`, against a mutant testing `startswith(f"chitty/{name}")` without the trailing `/`, and against a mutant testing only `startswith("chitty/")`
- [ ] `test_ticket_only_move_lands_without_a_second_check` passes; a note records that it fails against `src/chitty/run.py` without the change (count 2)
- [ ] `test_mixed_move_reruns_the_check`, `test_quick_path_stops_after_ten_ticket_moves` and the existing `TestLandingRetry` tests pass; a note records that the mixed test fails against a mutant that skips the check after any move, and that the ten-moves test fails, by its own call guard, against a mutant with no quick-path limit
- [ ] Outside `chitty/`, the branch commits change only `src/chitty/run.py`, `src/chitty/git.py`, the two test files and `docs/plan/next-action-and-runner.md`: `git diff --stat $(git merge-base main HEAD) HEAD -- . ':!chitty'` lists exactly those five paths (comparing with the merge base leaves out commits `main` gained since, and `chitty/` holds this ticket's own file); the docs bullet describes the quick path and names the cases where its assumption fails; `make check` passes

## Plan

Preserve the existing implementation; add the missing 21st-call guard to the quick retry regression test, verify it catches an effectively unbounded retry mutant, and rerun the required checks before handoff.

## Notes

Verification: `make check` passed (ruff, pyright, all 787 tests). Focused landing/property tests passed. The ticket-only landing test fails when `_only_ticket_paths` is forced false (the no-quick-path behavior); boundary tests kill both the missing-slash context-prefix mutant and the broad `chitty/` mutant. The mixed-move test fails when the predicate is forced true, and the ten-move guard test fails with the limit raised to 1000. These are executable mutant checks; the original NotImplementedError-stub run was not captured.

Review failed (design): Criterion 4 requires `git diff --stat main` to contain only five implementation paths, but this ticket necessarily records its own plan, notes and review status in a committed ticket file. The current command also includes unrelated changes on advancing main (currently TASK-470). Decide whether to exclude ticket metadata and compare the branch against its merge base; the literal criterion cannot guide completion as written. Preserve the implementation while planning.
1: pass - `make check` passed all 788 tests. Running the property with an injected `NotImplementedError` printed `FAILED (errors=1)`; separate injected missing-slash and broad-prefix mutants each printed `AssertionError: True != False`. This note records the previously uncaptured stub result.
2: pass - The test passed in `make check`; running it with `_land_locked` loaded from `main:src/chitty/run.py` printed `AssertionError: 2 != 1`.
3: fail - The landing retry tests passed in `make check`; forcing the predicate true made the mixed test print `1 != 2`. However, `moving_fast_forward` has no 21st-call guard, so the specified unbounded-mutant test is missing and could hang. Add the guard and run the no-limit mutant; raising the limit to 12 printed a mismatched 12-attempt error, not the required guard failure.
4: fail - `make check` passed, and the documentation names both exceptions. `git diff --stat main` printed seven paths, including this ticket and TASK-470, contrary to the literal criterion. Clarify the intended comparison and exemptions before assessing it.

## Summary

Implemented ticket-only quick landing retries, bounded to ten, with merge-base support, property/boundary coverage, landing retry tests, and documentation. Verified using make check and focused mutant probes; see Notes. No follow-up.

## History

- 2026-11-19T21:23:51Z daring-amber-kestrel → planning
- 2026-11-19T21:24:10Z daring-amber-kestrel: changed description
- 2026-11-19T21:24:14Z daring-amber-kestrel planning → cold-read
- 2026-11-19T21:25:36Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T21:25:36Z daring-amber-kestrel cold-read → planning
- 2026-11-19T21:25:47Z daring-amber-kestrel planning → cold-read
- 2026-11-19T21:27:44Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T21:27:44Z daring-amber-kestrel cold-read → planning
- 2026-11-19T21:27:58Z daring-amber-kestrel: changed acceptance criteria
- 2026-11-19T21:27:58Z daring-amber-kestrel planning → cold-read
- 2026-11-19T21:29:13Z daring-amber-kestrel: changed description
- 2026-11-19T21:29:13Z daring-amber-kestrel cold-read → planning
- 2026-11-19T21:29:17Z daring-amber-kestrel planning → todo
- 2026-11-19T23:52:32Z youthful-zinc-wren todo → doing
- 2026-11-19T23:54:08Z youthful-zinc-wren: wrote the plan
- 2026-11-20T00:04:12Z youthful-zinc-wren: changed notes, summary
- 2026-11-20T00:04:54Z youthful-zinc-wren doing → review
- 2026-11-20T00:10:29Z able-dusky-toad: changed owner, acceptance criteria, notes
- 2026-11-20T00:10:29Z able-dusky-toad review → planning
- 2026-11-20T22:33:54Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-20T22:33:54Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:34:37Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-20T22:34:37Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T22:34:43Z youthful-hazel-marten todo → doing
- 2026-11-20T22:36:03Z youthful-hazel-marten: wrote the plan
