---
title: Add a `cold_read_model` setting
status: backlog
parent: TASK-259
created: 2026-11-11
---

## Description

- Like `work_model` and `review_model` (`src/chitty/config.py`, `_model_arguments` in `src/chitty/run.py`): the model passed to cold-read sessions when the command names none.
- Cold reads should run on a weak model (Haiku, Luna). This repository sets it once the setting lands, in the main checkout.

## History

- 2026-11-11T13:21:07Z vivid-yellowhammer → backlog
