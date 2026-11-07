---
title: Refuse `--ac` and `--rm-ac` while a task is in review
status: backlog
created: 2026-11-07
---

## Description

Found by the second cold read of `TASK-226` on 2026-11-07. A reviewer can add or remove acceptance criteria while a task is in `review`, then pass it with verdicts on criteria the worker never saw, or without the ones removed. `TASK-226` refuses its new `--set-ac` in that state; `--ac` and `--rm-ac` are not guarded. Decide whether to refuse them the same way, in `check_edit` in `src/chitty/store.py`.

## History

- 2026-11-07T10:09:05Z vivid-dormouse → backlog
