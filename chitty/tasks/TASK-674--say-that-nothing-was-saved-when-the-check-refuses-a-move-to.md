---
title: Say that nothing was saved when the check refuses a move to `review`
status: planning
labels:
  - bug
created: 2026-11-24
---

## Description

### Why

When `chitty edit <ID> -s review --summary-file F` is refused because the configured check fails, the whole edit is dropped, including the summary, and the error does not say so. On 2026-11-23, TASK-643 to TASK-646 hit this. Their worktrees were made by hand with `git worktree add`, so the configured `setup` (`make install`) had not run, and pyright could not resolve the `mcp` extra. Rerunning setup fixed the check, but every summary had to be rewritten from scratch.

### Change

In `Repo.edit` in `src/chitty/store.py` (around lines 1020-1057), every refusal raised while entering `review` gets the sentence `Nothing from this edit was saved.` at the end, after `; ` or `. ` as fits its wording. That covers:

- the check failing (`check failed with status N; output in .chitty/check.log`);
- the check timing out (`commands.CommandTimedOut`);
- the check command not being found;
- `require_clean()` refusing, both before and after the check.

When the check fails (non-zero status only) and `self.config.setup` is set, add a sentence after that: ``If this worktree was never set up, run `<setup>` first.``

Decided: the edit stays all-or-nothing. Saving the summary and notes while refusing only the status would make one command do half its work, and a later `-s review` would need them again anyway. The caller is told to keep the text instead.

Keep the wording in one small pure helper in `store.py`, for example `_review_refusal(reason: str, setup: str | None, *, check_failed: bool) -> str`, so the four call sites cannot drift.

### Tests

No property: the input is a small fixed set (four refusals, and setup set or not), each listed and tested. The tests extend `tests/test_review_check.py`, whose `prepare` makes branch `task-1` with the ticket in `doing`. Pass `--summary Done.` with `-s review`, and check that the output has the new sentence and the ticket file has no Summary. Today the summary is already dropped, so only the message assertion fails without the change.

### Out of scope

Saving any part of a refused edit; running `setup` automatically.

## Acceptance Criteria

- [ ] In `tests/test_review_check.py`, `chitty edit 1 -s review --summary Done.` in the `test_failure`, `test_missing` and `test_dirty` setups each exits 1 with output containing `Nothing from this edit was saved.`, and the ticket file has no `## Summary` section afterwards. These fail without the change.
- [ ] With `setup` configured (for example `setup = "true"`), the `test_failure` case output also contains ``If this worktree was never set up, run `true` first.``; with no `setup` configured it does not contain `never set up`. The timeout refusal also ends with `Nothing from this edit was saved.`; test it with the existing `command_timeout` setting if a test can set it low, otherwise say in a note why not. `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:37Z zesty-coral-newt → backlog
- 2026-11-24T22:21:38Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:48Z zesty-coral-newt: changed labels
- 2026-11-24T22:59:48Z zesty-coral-newt: changed title, labels, description, acceptance criteria
- 2026-11-24T22:59:48Z zesty-coral-newt backlog → planning
