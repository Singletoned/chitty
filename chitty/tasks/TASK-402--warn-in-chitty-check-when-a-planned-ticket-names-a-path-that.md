---
title: Warn in `chitty check` when a planned ticket names a path that does not exist
status: backlog
created: 2026-11-18
---

## Description

Planners write claims about code from memory: in the 2026-11-18 ticket-state planning, cold reads spent rounds on a nonexistent `chitty restore` command, wrong test classes and similar (`docs/plan/pipeline-and-feedback.md`, Cold read). The plan guide says to run `chitty check` on a ticket before its cold read. Owner decision 2026-11-22: build whatever can be checked easily and reliably. That is backticked repository paths; identifiers and commands are out of scope (too noisy to check without a language-aware index).

Decisions:

- New pure function `missing_paths(text: str, exists: Callable[[str], bool]) -> list[str]` in `src/chitty/check.py`. For each line of `text`, skip the line if it contains the word `new` (case-insensitive, matched with `\bnew\b`), since tickets introduce files they create that way ("a new `tests/test_x.py`"). Otherwise, for each code span on the line, matched with `` `([^`\n]+)` ``, take its text; drop a trailing `:<digits>` or `:<identifier>` (`:\d+` or `:[A-Za-z_]\w*`, so `src/a.py:12` and `src/a.py:main` check `src/a.py`). The result is a path candidate when it matches `[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+/?` in full (at least one `/`, no spaces, no glob or placeholder characters such as `*`, `<`, `{`), and does not start with `/`, `~`, `.` or `-`. Return each candidate for which `exists` is false, once, in first-seen order.
- In `check()` (`src/chitty/check.py`), for every ticket file it parses whose status is `planning`, `cold-read` or `todo`, run `missing_paths` over the Description and each criterion text, with `exists = lambda path: (repo.root / path).exists()` (the checkout running `chitty check`: a ticket worktree sees names its branch adds). Add one warning per missing path, on the ticket's file: ``names `<path>`, which does not exist in this checkout``. Warnings do not change the exit code.
- Out of scope: identifiers, commands, symbols inside files, tickets in other statuses.

Tests in a new `tests/test_check_missing_paths.py`.

- Property with Hypothesis (the repository's property tool) on `missing_paths`: draw a set of existing paths and a set of missing paths (each two or three parts from `st.text(alphabet=string.ascii_lowercase + "_", min_size=1, max_size=8)`, joined with `/`, missing ones built by appending `_gone` to a drawn part so they never equal an existing one), and a list of one to eight lines, each made of filler words (never `new`) and zero to three items: a backticked existing path, a backticked missing path (sometimes with `:12` or `:main` appended), or a backticked non-path (`chitty edit -s todo`, `TASK-5`, `src/*.py`, `<path>`, `README.md`); and, per line, whether to add the word `new` (in a drawn case: `new`, `New` or `NEW`). `exists` is membership in the existing set. Expected, computed from the draws: the missing paths on lines without `new`, once each, in first-seen order.
- CLI example inheriting `CliTestCase` from `tests/test_cli.py`: a `planning` ticket naming `src/chitty/nonexistent.py` and `src/chitty/check.py` in its description; `chitty check` exits 0 and warns about the first only; after `chitty edit -s todo` still warns; a `done` ticket naming the same path gives no warning.

## Acceptance Criteria

- [ ] The `missing_paths` property passes, and fails against a version that ignores the `new` rule and against one that keeps the `:12` suffix (commit both as mutant tests with `hypothesis.find`)
- [ ] The CLI example passes: one warning for the missing path in `planning` and `todo`, none for the existing path or a `done` ticket; this fails before the change; `make check` passes

## Notes

The description leaves three blocking design questions open: which backticked tokens count as code identifiers versus prose/commands; how to avoid flagging valid paths or identifiers a ticket intends to create; and whether lookup uses the current ticket branch, main, or both. The requested warning cannot be implemented or tested consistently until these are decided. In particular, a main-only lookup would miss names introduced on an active branch, while branch-only lookup could regard branch-specific work as valid; proposed paths need an explicit rule. Planner: define token/path recognition and exclusions, baseline semantics, and user-visible severity/failure behavior, then add verifiable acceptance criteria.

Question for the owner (2026-11-21, overnight planner): the worker's blockers above are policy choices, so they were not settled overnight. Proposal to confirm or change: (1) only backticked spans that look like a repository path (contain `/` or end in a known source extension) or a `file.py:symbol`/`module.function` reference count; (2) check them against the tree of the checkout running `chitty check` (the ticket branch in a worktree, `main` in the main checkout), so names a branch adds are found; (3) a warning, never an error, and skipped for tickets that are `done` or archived. Is this worth building, and are these the right rules?

Owner answer, 2026-11-22: build whatever can easily be automated. Planner: paths only, existence in the checkout running `chitty check`, warnings only, lines with the word `new` skipped.

Planner, 2026-11-22: measured before building. The path rule in the Description, run over every `planning` and `todo` ticket on `main`, gave 10 warnings, 8 of them false alarms (example paths such as `src/a.py` in test fixtures, and files a ticket creates without the word `new` on the line). The narrower check of `file.py:symbol` and `file.py:12` references found 1 such reference in all open tickets. Neither is easily automated well enough to beat not having it, so this is parked. Owner to decide: close it, or keep the path check with a different exclusion rule.

Owner decision, 2026-11-22: not built. Neither check is easily automated well enough to beat not having it (see the measurement above); archived.

## History

- 2026-11-18T20:24:11Z lively-quartz-crane → todo
- 2026-11-18T23:24:21Z friendly-indigo-wren todo → doing
- 2026-11-18T23:25:30Z friendly-indigo-wren: changed owner, notes
- 2026-11-18T23:25:30Z friendly-indigo-wren doing → planning
- 2026-11-21T23:23:08Z lively-zinc-newt: changed labels, notes
- 2026-11-22T11:15:26Z friendly-jade-stoat: changed title, labels, description, acceptance criteria, notes
- 2026-11-22T11:15:26Z friendly-jade-stoat planning → cold-read
- 2026-11-22T11:17:14Z friendly-jade-stoat: changed labels, notes
- 2026-11-22T11:17:14Z friendly-jade-stoat cold-read → backlog
- 2026-11-22T11:23:44Z friendly-jade-stoat: changed labels, notes
