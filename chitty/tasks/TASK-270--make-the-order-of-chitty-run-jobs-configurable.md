---
title: Make the order of `chitty run` jobs configurable
status: cold-read
parent: TASK-259
created: 2026-11-11
---

## Description

- Today `src/chitty/selection.py` picks `review`, then `doing`, then `todo` (`STATUSES`). Add a top-level `job_order` setting in `chitty.toml`: a list of those statuses, in pick order. Unset means today's order.
- An entry that is not one of those statuses is a config error naming it. A status left out of the list is never picked.
- TASK-272 adds `cold-read` to the allowed statuses and puts it first in the default, because cold reads hold up planning.

## Acceptance Criteria

- [ ] With `job_order = ["todo", "review"]` and one ticket in each, `chitty next` picks the `todo` ticket; without the setting it picks the `review` ticket, as today.
- [ ] With `job_order = ["todo"]` and only a `review` ticket, `chitty next` prints `no next ticket`; `job_order = ["typo"]` fails with an error naming `typo`.

## History

- 2026-11-11T13:21:06Z vivid-yellowhammer → backlog
- 2026-11-11T13:39:43Z vivid-yellowhammer: changed description, acceptance criteria
- 2026-11-11T13:39:50Z vivid-yellowhammer backlog → cold-read
