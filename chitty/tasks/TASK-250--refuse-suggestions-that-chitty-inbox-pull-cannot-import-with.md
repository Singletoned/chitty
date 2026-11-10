---
title: Refuse suggestions that `chitty inbox --pull` cannot import, with a property test
status: done
depends_on:
  - TASK-249
created: 2026-11-10
---

## Description

Second of two trial tickets for property tests.

**Property:** any suggestion that `inbox.suggest` accepts, `inbox.pull` imports, and the new ticket's title and Description equal what was sent. Normalise the Description as `pull` does: strip it, right-trim each line, and use `store.BACKLOG_DESCRIPTION` when it is empty.

**Fails today.** Each of these is accepted, then fails every later pull, because a pull is all or nothing:

- an empty title, a title containing U+2028, or one containing a C1 control such as `\x84`;
- a title ending in `---`: `_read_suggestion` splits the file on `---\n`, so pull raises `KeyError: 'created'`;
- a description with a text line followed by a `---` line (a setext heading).

**Fix:**

- `suggest` builds the ticket it would create with `model.new_task`, using the normalised Description, and raises that error as a `ChittyError` before writing anything. It still writes the text as given.
- `_read_suggestion` finds the frontmatter by its `---` delimiter lines, not by splitting on `---\n`.

Depends on TASK-249, whose re-parse check makes `new_task` reject `## Notes` lines, unclosed fences and form feeds in a Description. Those cases need it; the ones above do not.

**Test:** `tests/test_property_inbox.py`, inheriting `RepoTestCase`. One repository for the whole test, `project = "target"` in `chitty.toml` as `tests/test_inbox.py` does, `deadline=None`, about 50 examples. Draw Descriptions that include `## ` lines, fences and form feeds, which TASK-249 makes `new_task` reject. Count only `suggestion-*` files: `pull` also writes a registration file.

## Acceptance Criteria

- [x] The property test fails before the fix, on the inputs above or others the generator finds, and passes after.
- [x] `chitty suggest` with a U+2028 title, a title ending in `---`, or a setext-heading description exits non-zero and writes no suggestion file; a following `chitty inbox --pull` of another suggestion succeeds.

## Plan

Add a RepoTestCase property test covering accepted suggestions through pull and verifying imported title/normalised Description. First confirm it fails on current behavior. Update inbox.suggest to validate the exact normalized task via model.new_task before writing, and parse suggestion frontmatter using delimiter lines. Add CLI regression coverage for rejected inputs and all-or-nothing pull safety. Run make format and make check, then commit implementation changes with Task: TASK-250.

## Notes

Possible starting point: `refs/cold-read/TASK-250/2` (`git show refs/cold-read/TASK-250/2:<path>`). Check it against the criteria; don't trust it.

Property test initially exposed a real mismatch beyond the listed examples: U+0085 in a title was normalized during task rendering. Validation now rejects any candidate whose title or normalized Description fails to round-trip. The property test passed (50 examples), and make format && make check passed (455 Python tests plus Node tests). The initial pre-fix property run failed during pull for rejected title/Description examples; after refining to catch suggest rejections, pre-fix failure showed pull could fail for accepted titles. CLI-specific acceptance scenarios were not separately exercised.

Re-verified both criteria: the property suite passed with 50 examples; the CLI regression confirmed U+2028, trailing --- and setext-heading suggestions exit non-zero without writing files, then a valid suggestion pulled successfully. The CLI test initially exposed trailing --- being accepted despite the ticket requirement; suggest now rejects that delimiter-like title. /Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-131--land-reviewed-tickets-from-chitty-run.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-131--land-reviewed-tickets-from-chitty-run.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-144--mark-chitty-s-block-in-agents-md-with-strict-begin-and-end-c.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-148--log-usage-for-failed-and-interrupted-runs.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-169--find-what-leaves-temporary-projects-in-the-real-inbox.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-177--count-other-branches-tickets-when-allocating-an-id.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-179--stop-telling-workers-to-run-chitty-inbox-pull.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-179--stop-telling-workers-to-run-chitty-inbox-pull.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-181--put-the-literal-instruction-back-in-the-agent-prompts.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-181--put-the-literal-instruction-back-in-the-agent-prompts.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-182--cover-pyproject-toml-in-newer-key-tests-and-stop-version-par.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-191--keep-tickets-in-random-id-contexts-in-backlog.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-193--require-evidence-in-a-review-that-fails-a-ticket.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-193--require-evidence-in-a-review-that-fails-a-ticket.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-198--warn-in-chitty-check-about-indented-lines-inside-a-paragraph.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-199--exit-3-when-chitty-next-or-chitty-run-has-no-ticket.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-208--explain-the-setup-and-autocommit-errors-from-chitty-run.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-216--use-main-branch-instead-of-main-in-the-code.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-218--refuse-ticket-branches-that-change-agents-md-s-managed-block.md: warning: Notes contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-218--refuse-ticket-branches-that-change-agents-md-s-managed-block.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-222--leave-every-owned-ticket-out-of-a-plain-chitty-run.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-222--leave-every-owned-ticket-out-of-a-plain-chitty-run.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-224--bump-the-version-at-release-not-on-ticket-branches.md: warning: Summary contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-237--compare-the-managed-agents-md-block-with-the-merge-base-not.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-237--compare-the-managed-agents-md-block-with-the-merge-base-not.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-238--clear-virtual-env-and-uv-project-environment-for-setup-and-c.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-238--clear-virtual-env-and-uv-project-environment-for-setup-and-c.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-238--clear-virtual-env-and-uv-project-environment-for-setup-and-c.md: warning: Summary contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-246--time-out-the-agent-started-by-chitty-run.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-63--stop-prefixing-every-git-error-with-autocommit-failed.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-63--stop-prefixing-every-git-error-with-autocommit-failed.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/TASK-72--show-status-glyphs-and-why-chitty-next-skips-a-ticket-in-chi.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-1--reject-setext-headings-in-task-bodies.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-124--add-chitty-next-and-chitty-run-to-do-the-next-ticket.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-126--chitty-run-prepares-the-worktree-and-claim-before-starting-p.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-129--do-not-install-the-pi-extension-from-a-linked-worktree.md: warning: Notes has an indented line inside a paragraph; put pasted output in a fenced code block
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-15--add-bash-and-zsh-completion.md: warning: Description contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-178--stop-chitty-run-from-a-ticket-worktree-changing-main-s-setup.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Plan contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Notes contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-184--pick-the-right-copy-of-a-ticket-when-commits-share-a-second.md: warning: Summary contains literal '_' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-45--write-chitty-toml-inline-comments-with-a-single-space.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-47--guide-tells-agents-to-put-paths-globs-and-code-in-backticks.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-49--warn-in-chitty-check-when-task-text-has-markdown-characters.md: warning: Description contains literal '*' Markdown delimiter; use backticks for code
/Users/singletoned/src/singletoned/chitty/.worktrees/task-250/chitty/tasks/archive/TASK-56--remove-prefix-from-chitty-init-prefixes-name-queues-not-proj.md: warning: Acceptance Criteria #2 contains literal '*' Markdown delimiter; use backticks for code, make format, and make check passed (456 Python tests and Node tests).

Review failed (tests): The property generator explicitly filters out Description lines beginning with `## ` or fences and any form feed, although the ticket requires drawing those cases. Add generated examples for all three and verify rejection as well as accepted round trips. Also isolate or clean up each failed example so Hypothesis can replay and shrink it: running the property test with the pre-fix inbox printed `FlakyFailure: Inconsistent results from replaying a test case`, first `TaskError: title: must not be empty`, then `KeyError: created`, because failed pulls leave suggestions behind. `make format && make check` passed (459 Python tests and Node tests).

1: fail - Required Description cases are excluded and failing examples contaminate replay.
2: pass - CLI regression passed in the full check.

Review failed (tests): Inspection of tests/test_property_inbox.py shows DESCRIPTION_LINES filters out lines beginning with `## `, fences, and form feeds in _safe_description_line; it only separately includes `---`. Therefore the property does not draw the TASK-249 rejection cases required by criterion 1, nor verify they are rejected without polluting replay. `make format && make check` passed (459 Python tests and Node tests), but these tests do not cover that requirement.

Expanded the property generator and explicit examples to cover heading lines, unclosed fences, and form feeds; failed pulls clean up only that example’s new suggestions so Hypothesis replay/shrinking is stable. Confirmed regression: with inbox.py temporarily restored from 9f9d887, `uv run python -m unittest tests.test_property_inbox -v` failed on explicit malformed-description examples during pull. Restored implementation and reran property test successfully. Rechecked CLI scenario with `uv run python -m unittest tests.test_cli.TestInbox.test_unimportable_suggestions_are_rejected_without_poisoning_pull -v`; passed. `make format && make check` passed (459 Python tests and Node tests).

Reviewed: make format && make check passed (459 Python tests and Node tests). The property test failed against the pre-fix inbox with an unclosed fence during pull, and passed with the fix.

1: pass - Generated and explicit cases exercise accepted round trips and rejected suggestions.
2: pass - CLI regression covers the three inputs and subsequent pull; the property test checks rejected suggestions leave no files.

## Summary

Handoff: property coverage now explicitly includes required TASK-249 invalid Description forms and cleanup avoids leftover suggestions on failed pull. Verified pre-fix regression failure, post-fix property and CLI tests, and full make format/check (459 Python tests plus Node tests). Follow-ups: none.

## History

- 2026-11-10T21:12:38Z jolly-heron → backlog
- 2026-11-10T21:17:27Z jolly-heron: replaced notes; changed description, acceptance criteria
- 2026-11-10T21:21:56Z jolly-heron: changed description, notes
- 2026-11-10T21:21:56Z jolly-heron backlog → todo
- 2026-11-10T21:58:53Z jolly-heron: replaced notes
- 2026-11-10T22:37:01Z eager-raven todo → doing
- 2026-11-10T22:37:16Z eager-raven: wrote the plan
- 2026-11-10T22:39:52Z eager-raven: changed notes; ticked acceptance criteria
- 2026-11-10T22:41:28Z eager-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-10T22:41:28Z eager-raven doing → review
- 2026-11-10T22:44:17Z zesty-dormouse: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-10T22:44:17Z zesty-dormouse review → doing
- 2026-11-10T23:00:57Z open-marten: changed acceptance criteria, notes
- 2026-11-10T23:02:59Z open-marten: changed notes, summary; ticked acceptance criteria
- 2026-11-10T23:02:59Z open-marten doing → review
- 2026-11-10T23:06:50Z daring-crane: changed notes; ticked acceptance criteria
- 2026-11-10T23:06:50Z daring-crane review → done
