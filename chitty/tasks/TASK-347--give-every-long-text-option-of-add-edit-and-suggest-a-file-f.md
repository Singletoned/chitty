---
title: Give every long text option of add, edit and suggest a file form
status: doing
created: 2026-11-16
---

## Description

Agents pass long ticket text as shell arguments, and the guides spend a paragraph each on quoting backticks and apostrophes. `chitty edit` has `--description-file`, `--plan-file`, `--note-file` and `--set-notes-file`. Their `click.File()` type already reads stdin for `-`, but only `--note-file` says so. `chitty add` has only `--note-file`, `chitty edit` has no `--summary-file`, and `chitty suggest` has only `-d`, so long text goes through `-d "$(cat file)"` (seen 2026-11-12 on `TASK-302` and 2026-11-17).

Decisions:

- Add `--description-file` to `chitty add` and `chitty suggest`, and `--summary-file` to `chitty edit`, each combined with its text option through `_text` in `src/chitty/cli.py`, so giving both is the existing usage error. In `add`, resolve the description file before the `--description is required` check.
- Every `-file` option of the three commands, old and new, uses `click.File(encoding="utf-8")`, so non-ASCII text does not depend on the locale.
- Every `-file` option of `add`, `edit` and `suggest` says `('-' for stdin)` in its help.
- Two `-file` options in one command both given `-` is a `click.UsageError` naming them, because the second would silently read nothing. Check it in one helper in `cli.py` that each command calls with all its `-file` options, `--note-file` included. A text option and a different `-file` option together stay allowed, for example `--note` and `--note-file`.
- `--ac` and `--set-ac` get no file form: criteria are one line each.
- `cli.py` stays thin: no change to `store.py`, `mcp.py` or `inbox.py`.
- Replace the quoting advice (the text starting `Backticks run commands inside double-quoted shell arguments`) in `src/chitty/guide.md`, `src/chitty/roles/work.md`, `review.md` and `plan.md` with one line: ``Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.`` Update `tests/test_guide_backticks.py` to that line, and `tests/fixtures/guide-before-workflow.md` only if a test fails without it. Do not change `AGENTS.md` on the branch: after this lands, the main checkout's `chitty init` refreshes the managed block, and the planning session updates the hand-written copy in the `## Chitty` section.
- Update the option lists in `docs/plan/cli.md` and the stdin mention in `docs/plan/task-file.md`.
- `TASK-306` (`--description-file` for `chitty add`) is superseded and gets archived by the planning session when this lands.

Tests: a Hypothesis property in a new `tests/test_property_text_files.py`, in a class inheriting `RepoTestCase` (the inbox must not be touched), using Click's `CliRunner` as `tests/test_cli.py` does. Text is generated from `a`, `b`, `1`, a space, a newline, a backtick, `'`, `"`, `$`, `\`, `*` and `é`, with at least one letter: filtered to never contain three backticks in a row; with no `#` or `~` in the alphabet the text never starts a heading or fence, and the letter means it is never whitespace-only, which the store refuses. For each example, create a fresh repository in a new temporary directory under the test's own (with one seeded ticket for `edit`, created by `add T -d x --json`; the `CONFIG` in `tests/support.py` has no `random_ids`, so `add` requires a description), and run each text option three ways: inline, from a UTF-8 file, and from `-` with that text on stdin. The three runs must leave the same `description`, `plan`, `notes`, `summary` and `criteria` in `chitty show --json` (History differs by timestamp, so compare those fields only). It covers `add -d`, `add --note`, `edit -d`, `--plan`, `--note`, `--set-notes` and `--summary`. Each `add` run is `add T --json` plus the option under test, with `-d x` added when the option is not the description; read the created ticket by the `id` from that JSON with `show <id> --json`. Each `edit` run edits the seeded ticket and then reads it with `show --json`. All three runs pass exactly the same generated text, so whatever the store normalises (it strips trailing whitespace on each line) applies equally to each. Run and report each option as its own arm (for example one test method or `subTest` per option), so a reviewer can see which arms fail before the change: only `add -d` (no `--description-file` yet) and `edit --summary` (no `--summary-file` yet) fail; the other arms already have file forms and pass. Keep `max_examples` small (25) because each example runs the CLI. `suggest` is not in the property. Example tests in the same file: `suggest <self.root.name> T --description-file -` (after `chitty init`, as `test_inbox_lists_and_pulls_suggestions` in `tests/test_cli.py` does) leaves the same `description` in `chitty inbox --json` as `suggest <self.root.name> T -d` with the same text, and two `-` options in `add` and in `edit` are refused naming both (`suggest` has only one `-file` option, so it has no such case). Also: `add T --note-file -` with the note on stdin and no `-d` exits with `--description is required unless --status backlog`, and `add T --description-file -` with the description on stdin and no `-d` creates the ticket with that description.

Out of scope: MCP, file forms for criteria or titles, and reading files relative to anything but the working directory.

## Acceptance Criteria

- [ ] The Hypothesis property in `tests/test_property_text_files.py` shows each listed text option and its `-file` form, from a file and from `-`, write the same ticket, one arm per option; the `add -d` and `edit --summary` arms fail before the change and the others pass
- [ ] `suggest --description-file -` leaves the same inbox description as `-d`; `add --description-file -` with no `-d` creates the ticket; giving `-` to two `-file` options of `add` or of `edit` exits with a usage error naming both; the tests fail before the change
- [ ] The four guides carry the one-line file advice in place of the quoting advice; every `-file` option of `add`, `edit` and `suggest` is `click.File(encoding="utf-8")` and its help contains `('-' for stdin)`; `docs/plan/cli.md` lists the new options; `make check` passes

## Plan

Add the specified per-option property and example tests, verify their pre-fix failures, then implement UTF-8 file options and stdin conflict validation in the CLI. Update guide and plan documentation, run fix, format and checks, and commit the implementation.

## Notes

Cold read by a Haiku subagent, 2026-11-17. Fixed: `add` checks the required description before reading a file; the property generator could produce text the store refuses whatever the option; History timestamps made "same ticket file" unverifiable; per-example repositories and `RepoTestCase`; UTF-8 file encoding; where the two-stdin check lives; the docs to update. Not adopted: none.

The unfinished CLI work from 2026-11-17 is saved as tag `task-347-partial` (commit `8180e62d`). It was 1324 commits behind `main` and no longer applies, so the stale worktree and branch were removed: start fresh from `main`, using that tag only as a reference.

Before the fix, the property arms for add description and edit summary failed on missing file options; the other five arms passed. The stdin examples also failed on missing options or the missing conflict check.

## Summary

Implemented UTF-8 long-text file options, stdin conflict validation, guide and plan documentation, and property and example coverage. Before the fix, the two new-option property arms and stdin examples failed; the other property arms passed. `make check` passes all 852 tests. The guide fixture required updating after the workflow guide tests failed. Planning should archive superseded TASK-306 and refresh the hand-written guide after landing.

## History

- 2026-11-16T09:59:58Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:41Z intrepid-coral-raven backlog → planning
- 2026-11-17T17:52:25Z kind-umber-toad: changed title, description
- 2026-11-17T19:59:02Z kind-umber-toad: changed title, description, acceptance criteria
- 2026-11-17T19:59:05Z kind-umber-toad: changed owner
- 2026-11-17T19:59:05Z kind-umber-toad planning → cold-read
- 2026-11-17T19:59:14Z kind-umber-toad: changed acceptance criteria
- 2026-11-17T20:01:10Z kind-umber-toad: changed description, acceptance criteria, notes
- 2026-11-17T20:01:10Z kind-umber-toad cold-read → planning
- 2026-11-17T22:01:56Z kind-umber-toad: changed owner
- 2026-11-17T22:01:56Z kind-umber-toad planning → todo
- 2026-11-20T21:55:54Z quick-pearl-lapwing: changed notes
- 2026-11-20T21:55:54Z quick-pearl-lapwing todo → cold-read
- 2026-11-20T21:57:03Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T21:58:02Z quick-pearl-lapwing: changed description
- 2026-11-20T21:58:14Z quick-pearl-lapwing: changed description
- 2026-11-20T21:58:59Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-20T21:58:59Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T21:59:51Z calm-white-ibis todo → doing
- 2026-11-20T22:01:08Z calm-white-ibis: wrote the plan
- 2026-11-20T22:02:56Z calm-white-ibis: changed notes
- 2026-11-20T22:07:12Z calm-white-ibis: changed summary
