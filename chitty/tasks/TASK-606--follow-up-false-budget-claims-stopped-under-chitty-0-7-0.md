---
title: "Follow-up: false budget claims stopped under Chitty 0.7.0"
status: backlog
created: 2026-11-23
---

## Description

Follow-up to "Workers falsely claim insufficient budget and block tickets" (taidy, 2026-11-23). After the branches were reset to `main`, a single `chitty run --ticket TASK-24 -- --model gpt-6.1-terra` with Chitty 0.7.0 (the chitty checkout venv) ran the same ticket that had failed under 0.6.1. It implemented it in one session at about 40 thousand tokens, ran make test, typecheck, check and test-docker, and set `review`. So 0.7.0 (its rebase of the existing worktree before work, or its revised work prompt) removes the trigger in this case. Keep the prompt and blocked-note guard from the first suggestion, because the model still invented a budget limit when it stalled. Also note that 0.7.0 is not on PyPI (latest 0.6.1), so runners installed with `uv tool install chitty` still get the broken behaviour; publishing 0.7.0 would fix them.

## Notes

Suggestion origin: taidy

Folded into TASK-624; 0.7.1 is now on PyPI.

## History

- 2026-11-23T10:23:56Z witty-russet-gannet → backlog
- 2026-11-23T10:23:57Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:36Z witty-russet-gannet: changed notes
