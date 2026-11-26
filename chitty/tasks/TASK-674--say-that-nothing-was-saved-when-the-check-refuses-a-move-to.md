---
title: Say that nothing was saved when the check refuses a move to `review`
status: doing
labels:
  - bug
created: 2026-11-24
---

## Description

### Why

When `chitty edit <ID> -s review --summary-file F` is refused because the configured check fails, the whole edit is dropped, including the summary, and the error does not say so. On 2026-11-23, TASK-643 to TASK-646 hit this. Their worktrees were made by hand with `git worktree add`, so the configured `setup` (`make install`) had not run, and pyright could not resolve the `mcp` extra. Rerunning setup fixed the check, but every summary had to be rewritten from scratch.

### Change

In `Repo.edit` in `src/chitty/store.py`, the block guarded by `if (entering_review or passing_review) and (self.root / ".git").exists() and not edit.skip_current_version:` (around lines 1013-1059) can refuse in several ways: `_require_current_version` (before and after the check), `require_clean()` (before and after the check), check timed out, check command not found, and check failed. Every `ChittyError` raised from that block, for entering `review` and for `review` → `done` alike, gets the sentence `Nothing from this edit was saved.`: if the existing message does not end with a period, add one, then a space and the sentence. Git or configuration errors raised inside the block get it too, which stays true because nothing is written before the block ends. Do it in one place: wrap the block's body in `try`/`except ChittyError as error:` and raise a new `ChittyError` with the extended message, `from error`. Messages keep their existing text, for example the check-failed message still ends with its path to `.chitty/check.log` before the new sentence.

Only for a failed check (non-zero status), when `self.config.setup` is set, add one more sentence after that: ``If this worktree was never set up, run `<setup>` first.``

Decided: the edit stays all-or-nothing. Saving the summary and notes while refusing only the status would make one command do half its work, and a later `-s review` would need them again anyway. The caller is told to keep the text instead.

### Tests

No property: the input is a small fixed set (the refusals listed in the criteria, and setup set or not), each listed and tested. The tests extend `TestReviewCheck` in `tests/test_review_check.py`, whose `prepare` configures the check and makes branch `task-1` with the ticket in `doing`. For the timeout case, insert `command_timeout = 1` into `chitty.toml` after the `autocommit = true` line that `ReviewMergeTestCase.setUp` (`tests/test_review_merge.py`) writes, and commit it on `main` before `prepare`. For the `review` → `done` case, use `prepare(self.script(""))` so the check passes, move the ticket to `review`, and only then create the untracked file. Build the expected setup text from the `setup = ...` value the test reads back from `chitty.toml`; do not hard-code it. `command_timeout` is an integer number of seconds (`src/chitty/config.py`). Today the summary is already dropped, so only the message assertions fail without the change; still assert there is no `## Summary`, because `assert_doing` only checks the status.

### Out of scope

Saving any part of a refused edit; running `setup` automatically; refusals outside that block.

## Acceptance Criteria

- [ ] In `tests/test_review_check.py` (`TestReviewCheck`, using its `prepare`), `chitty edit 1 -s review --summary Done.` exits 1 with output containing `Nothing from this edit was saved.` in each of these cases: worktree already dirty (an untracked file created after `prepare`, so `require_clean` refuses before the check runs), check fails (`test_failure` setup), check command not found (`test_missing` setup), check leaves the worktree dirty (`test_dirty` setup), and check times out (`command_timeout = 1`, check sleeps 5 seconds). After each, the ticket file contains `status: doing` and no `## Summary`. One more case: with the ticket moved to `review` by a passing check and an untracked file created afterwards, `chitty edit 1 -s done --note Reviewed.` exits 1, its output contains the sentence, and the ticket file still contains `status: review`. These fail without the change.
- [ ] In the check-fails case the output also contains ``If this worktree was never set up, run `<setup>` first.``, with `<setup>` the `setup` command `ReviewMergeTestCase.setUp` writes; in the not-found, dirty and timeout cases the output does not contain `never set up`; and after the test deletes the `setup = ...` line from `chitty.toml` and commits on `main` before `prepare`, the check-fails output does not contain `never set up`. `make check` passes.

## Notes

Requeued 2026-11-26: the last worker returned it after emptying `src/chitty/store.py` by accident; this worktree is clean at the committed version, so start from it. No ticket defect was found.

## History

- 2026-11-24T22:21:37Z zesty-coral-newt → backlog
- 2026-11-24T22:21:38Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:48Z zesty-coral-newt: changed labels
- 2026-11-24T22:59:48Z zesty-coral-newt: changed title, labels, description, acceptance criteria
- 2026-11-24T22:59:48Z zesty-coral-newt backlog → planning
- 2026-11-24T23:00:06Z zesty-coral-newt: changed description, acceptance criteria
- 2026-11-24T23:00:13Z zesty-coral-newt planning → cold-read
- 2026-11-24T23:02:00Z zesty-coral-newt: changed description, acceptance criteria
- 2026-11-24T23:02:00Z zesty-coral-newt cold-read → planning
- 2026-11-24T23:02:18Z zesty-coral-newt: changed description
- 2026-11-24T23:02:18Z zesty-coral-newt planning → cold-read
- 2026-11-24T23:03:48Z zesty-coral-newt: changed description, acceptance criteria
- 2026-11-24T23:05:38Z zesty-coral-newt: changed description, acceptance criteria
- 2026-11-24T23:05:38Z zesty-coral-newt cold-read → todo
- 2026-11-24T23:22:19Z calm-white-raven todo → doing
- 2026-11-24T23:25:25Z calm-white-raven: wrote the plan
- 2026-11-24T23:25:59Z calm-white-raven: changed owner, notes
- 2026-11-24T23:25:59Z calm-white-raven doing → planning
- 2026-11-26T11:36:50Z brisk-bronze-adder: changed notes
- 2026-11-26T11:36:50Z brisk-bronze-adder planning → to-plan
- 2026-11-26T11:36:56Z brisk-bronze-adder to-plan → planning
- 2026-11-26T11:37:02Z brisk-bronze-adder: replaced notes; changed owner; wrote the plan
- 2026-11-26T11:37:02Z brisk-bronze-adder planning → todo
- 2026-11-26T11:41:15Z plucky-bronze-quail todo → doing
