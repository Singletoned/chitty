---
title: Warn about backticks in double-quoted arguments in the generated guidance
status: review
priority: medium
depends_on:
  - TASK-143
created: 2026-11-01
---

## Description

The generated AGENTS.md Chitty section says "Put paths, globs, commands, IDs and code in backticks", which steers agents into the trap below whenever they pass text on the command line in double quotes. Add a line next to it, for example: "Backticks run commands inside double-quoted shell arguments: pass such text in single quotes, or with `--note-file -` and a quoted heredoc (`<<'EOF'`)."

What happened (circuitry, commit 90a902f, task CIRCUIT-67, 2026-10-29): a reviewing agent ran something like

    chitty edit CIRCUIT-67 -s doing --note "Independent review: failed. Acceptance criterion 1 is unmet: `chitty list --all` reports CIRCUIT-68, CIRCUIT-69 and CIRCUIT-71 as `doing`, not `done`. ..."

The generated AGENTS.md guidance tells agents to put commands, IDs and code in backticks, but inside a double-quoted shell argument backticks are command substitution. The shell ran `chitty list --all` and pasted its full output (75 lines, every task CIRCUIT-1 to CIRCUIT-75) into the note, and the other backticked words (`doing`, `done`, a file path) ran as commands and vanished, leaving "reports ... as , not .". The agent noticed and appended a "Correction to the preceding note", but could not remove the broken one, so `chitty show CIRCUIT-67` is 129 lines, 91 of them notes, about 7 KB of which is the dump.

The instruction now lives in `src/chitty/guide.md` and `src/chitty/roles/plan.md`, but `work.md` and `review.md` have none, and workers and reviewers are who hit this. Add this to all four, not just where the instruction is: "Backticks run commands inside double-quoted shell arguments, so pass such text in single quotes. Avoid an apostrophe in the text, or write it as `'\''`." `TASK-143` rewrites `guide.md`, so this follows it. `TASK-67`'s `--note-file` is not built.

## Acceptance Criteria

- [ ] A test shows `chitty guide` and each role guide containing the backtick warning; `make check` passes.

## Plan

Add the shell-safety warning immediately after the backtick-formatting instruction in the generated guide and all three packaged role guides (`plan`, `work`, and `review`). Add focused guide-output regression coverage, including the version assertion required by the ticket. Keep version handling aligned with the repository's branch rules and run the full check suite before handoff.

## Notes

Suggestion origin: circuitry

Seen again in `docs/pi-token-usage.md` on `pi-token-analysis`, 2026-11-04: about 16 `bash` calls show `command not found` for words such as `chitty_version`, `Repo.finalize` and `todo`, so ticket notes have probably lost text. A worker's note also ran `make check` this way during `TASK-126`. The guidance now also lives in `src/chitty/roles/`, so add the line wherever the backtick instruction is. `TASK-67`'s `--note-file` is not built, so say single quotes only.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the ticket had no criteria, and following the instruction's location would have missed workers and reviewers. Mentioned apostrophes, which single quotes break on.

Implementation is committed in 1448354 (Task: TASK-68). Added the shell backtick warning to the generated guide and all `work`, `review`, and `plan` role guides, with `tests/test_guide_backticks.py`. The regression test failed before the guide changes and passes after them. `make format && make check` passes.

Blocked on the acceptance criterion requiring `__version__` to be above `main`'s: both this branch and `main` are `0.1.43`, but the repository instructions explicitly prohibit changing `src/chitty/__init__.py` on a ticket branch and require `make release` to choose published bumps. A maintainer must decide whether to revise the criterion or authorize a release/version change; no version file was edited.

Unblocked: TASK-224 moved version bumps to release, so the branch-version requirement no longer applies. Implementation and tests are committed; ready for review.

## History

- 2026-11-01 → backlog
- 2026-11-04T21:41:12Z mellow-newt: changed priority, notes
- 2026-11-04T21:44:40Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T21:44:41Z mellow-newt backlog → todo
- 2026-11-08T11:12:03Z calm-badger todo → doing
- 2026-11-08T11:12:24Z calm-badger: wrote the plan
- 2026-11-08T11:14:55Z calm-badger: changed notes
- 2026-11-08T11:14:55Z calm-badger doing → blocked
- 2026-11-08T13:05:00Z eager-puffin: changed acceptance criteria, notes
- 2026-11-08T13:05:00Z eager-puffin blocked → review
