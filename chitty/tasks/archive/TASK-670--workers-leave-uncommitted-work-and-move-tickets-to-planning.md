---
title: Workers leave uncommitted work and move tickets to planning against their own note
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

Seen in echonomicon on 2026-11-23/24 with work_model openai-codex/gpt-6-luna under 'chitty run --loop --mode work'. TASK-197: the worker edited src/echonomicon/publisher.py and four test files, committed nothing, wrote the note 'Returning to planning is not appropriate: requirements are actionable; continue.' and then moved the ticket doing -> planning. TASK-195: same, left subscriptions.py and title_keys.py modified and uncommitted; the next runner pre-check (make lint test) then failed on the dirty tree and the ticket went to error. TASK-196: a worker moved to planning with a note describing missing tests on a branch whose ticket had just been clarified (an implementation gap, so doing). Suggested fixes: (1) when a session ends, the runner refuses or reverts a doing->planning/blocked move whose note does not name a planning blocker, or at least flags the contradiction; (2) the runner commits leftover changes as a WIP commit on the ticket branch (or reports them loudly) before changing status, so the next session neither loses them nor runs checks against a half-edited tree; (3) the runner's pre-check distinguishes failures caused by uncommitted worktree changes from failures on main.

## Notes

Suggestion origin: echonomicon

Duplicate: merged into TASK-686 (sound tickets returned to planning), TASK-676 (leftover uncommitted edits) and TASK-585 (stall detection); the evidence is recorded there.

## History

- 2026-11-24T22:21:33Z zesty-coral-newt → backlog
- 2026-11-24T22:21:34Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:38Z zesty-coral-newt: changed labels, notes
- 2026-11-24T22:41:20Z zesty-coral-newt backlog → archived
