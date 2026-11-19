---
title: Land without a new check when `main` moved only by ticket-file commits
status: planning
priority: high
created: 2026-11-19
---

## Description

On 2026-11-19 `TASK-404` passed review and then failed to land twice: `main moved during each of the 3 landing attempts`. Each attempt in `_land_locked` (`src/chitty/run.py`) rebases the branch onto `main`, runs `setup` and the landing check (about a minute here), then tries `git.fast_forward`; when `main` moved meanwhile, it starts the whole attempt again, up to `LANDING_ATTEMPTS = 3`. Between 21:01:42 and 21:05:49 `main` gained 7 commits, all but one `chitty: edit ...` ticket commits from a planning session, so every attempt lost. Ticket files cannot change what the check tests, so a move made only of ticket-file changes should not cost a new check.

Decisions:

- Pure function `_only_ticket_paths(paths: Sequence[str], contexts: Sequence[str]) -> bool` in `src/chitty/run.py`: `True` when every path starts with `chitty/<name>/` for some `<name>` in `contexts` (`BACKLOG_DIR` from `src/chitty/config.py` is `chitty`; a context's directory is `chitty/<name>`, see `Repo` in `src/chitty/store.py` near line 247), including its `archive/` subdirectory; `True` for no paths. Anything else, such as `chitty.toml`, `chitty/<name>` itself or `chitty/<name>x/...`, is not a ticket path.
- In `src/chitty/git.py`: `merge_base(root: Path, first: str, second: str) -> str` (`git merge-base`), and `paths_changed(root: Path, old: str, new: str) -> list[str]` (`git diff -z --no-renames --name-only <old> <new>`, so a rename lists both sides).
- In `_land_locked`, when `git.fast_forward` fails and `main` has moved (`not git.is_ancestor(main_root, main_branch, branch)`, as today): let `base = git.merge_base(main_root, branch, main_branch)`, the commit the checked branch was rebased onto. If `_only_ticket_paths(git.paths_changed(main_root, base, main_branch), list(main_repo.config.contexts))`, rebase onto `main` again (a conflict raises the same `cannot land ...; rebasing onto ... conflicts in ...` error as today) and try `git.fast_forward` again without running `setup` or the landing check. Repeat this quick path while `main` keeps moving by ticket files only, at most `QUICK_LANDING_ATTEMPTS = 10` times in all (a new module constant next to `LANDING_ATTEMPTS`); after that, raise `main moved during each of the 10 quick landing attempts`. When the new commits change any other path, fall back to today's full attempt, which counts toward `LANDING_ATTEMPTS` as now.
- The `chitty.toml` and protected-file refusals need no rerun on the quick path: a ticket-only move changes neither.
- Docs: add one bullet near the landing bullets in `docs/plan/next-action-and-runner.md` describing the quick path and its assumption: the landing check does not depend on ticket files (a repository whose check validates tickets, for example with `chitty check`, should know the quick path skips it). A probe on 2026-11-19 with the `ticket` mode below against today's code ran the check twice and then landed.

Tests:

- New `tests/test_property_landing_paths.py`, with Hypothesis (already a dependency, see `tests/test_property_ticket_source.py`): draw one to three distinct context names matching `CONTEXT_NAME_RE` in `src/chitty/config.py` and not in `RESERVED_CONTEXT_NAMES` (which holds `archive`) and a list of paths, each either a ticket path (`chitty/<name>/<rest>`, `<rest>` one or more segments, sometimes under `archive/`) or a non-ticket path built from a drawn name so it can never be a ticket path by chance: `chitty/<name>`, `chitty/<name>.d/<rest>`, `x/chitty/<name>/<rest>`, `chitty.toml`, `src/<rest>`. A context name cannot contain `.`, so `chitty/<name>.d/` is never another drawn context's directory (a suffix such as `x` could be: contexts `a` and `ax`). Property: the result is `True` exactly when every drawn path was built as a ticket path, and does not depend on the order of the list. Add the `NotImplementedError` stub of `_only_ticket_paths` first, so the tests fail on behaviour.
- In `tests/test_landing_retry.py` (`TestLandingRetry`), add a `run_script` mode `ticket`: on its first run only, the check copies `TASK-1`'s file on `main` to `chitty/tasks/TASK-9--moved.md` and commits it on `main` (as the `once` mode commits `check-1.txt`). New test `test_ticket_only_move_lands_without_a_second_check`: `finish_ticket()`, then `land_with_script("ticket")`. The count file has exactly one line, `main` contains the check's commit and the branch's commits, and the worktree and branch are gone. Today the count is 2.
- Mode `mixed`: like `ticket`, but the same commit also adds `check-1.txt`. New test `test_mixed_move_reruns_the_check`: the count is exactly 2 and the ticket lands. New test `test_quick_path_stops_after_ten_ticket_moves`: with `unittest.mock.patch`, wrap `chitty.run.git.fast_forward` so each call first commits a new ticket file `chitty/tasks/TASK-<20+n>--moved.md` on `main` (a copy of `TASK-1`'s file), then calls the real function; land with a check that only appends to the count file. It raises `main moved during each of the 10 quick landing attempts`, the count file has exactly one line, and the worktree and branch remain. Existing `test_retries_when_main_moves_once` and `test_stops_after_three_main_moves` must still pass unchanged: they move `main` with non-ticket files.

Out of scope: planning on branches, `TASK-428`'s lock, and the landing check itself.

## Acceptance Criteria

- [ ] The `_only_ticket_paths` property in `tests/test_property_landing_paths.py` passes, generating every path shape in the Description; a note records that it fails while the function raises `NotImplementedError`, and against a mutant that tests `startswith("chitty/<name>")` without the trailing `/`
- [ ] `test_ticket_only_move_lands_without_a_second_check` passes; a note records that it fails against `src/chitty/run.py` without the change (count 2)
- [ ] `test_mixed_move_reruns_the_check`, `test_quick_path_stops_after_ten_ticket_moves` and the existing `TestLandingRetry` tests pass; a note records that the mixed test fails against a mutant that skips the check after any move, and the ten-moves test against a mutant with no quick-path limit (it must then be stopped by the test's own guard, not hang: give the wrapper a call limit of 20 that raises)
- [ ] `git diff --stat` touches only `src/chitty/run.py`, `src/chitty/git.py`, the two test files and `docs/plan/next-action-and-runner.md`, where one landing bullet describes the quick path; `make check` passes

## History

- 2026-11-19T21:23:51Z daring-amber-kestrel → planning
- 2026-11-19T21:24:10Z daring-amber-kestrel: changed description
- 2026-11-19T21:24:14Z daring-amber-kestrel planning → cold-read
- 2026-11-19T21:25:36Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T21:25:36Z daring-amber-kestrel cold-read → planning
