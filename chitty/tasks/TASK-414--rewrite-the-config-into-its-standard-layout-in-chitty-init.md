---
title: Rewrite the config into its standard layout in `chitty init`
status: backlog
created: 2026-11-19
---

## Description

Today `chitty init` adds each missing setting as one block at the end of the Chitty section (`_add_missing_settings` in `src/chitty/store.py`), so an upgraded config drifts from a fresh one: related keys end up apart, and every new setting raises the question of where it goes (seen in `TASK-401`, which went through three failed reviews over splicing `rebase_model` next to `review_model`). Instead, rewrite the whole config in a standard order, grouping related keys and adding the commented-out lines for unset optional settings, keeping every value and the user's own comments. Owner decided 2026-11-19 that Chitty should be able to do this. Open question for planning: run it as part of every `chitty init`, or as a separate command; `init` already upgrades config, which keeps the command surface small.

## History

- 2026-11-19T10:01:39Z quick-ginger-lapwing → backlog
