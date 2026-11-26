---
title: Add an `old_prefixes` setting to contexts
status: cold-read
labels:
  - needs-minor
parent: TASK-W74AVC
created: 2026-11-26
provisional: true
---

## Description

### Why

Part of TASK-W74AVC: restarting numbering under a new prefix needs each context to remember the prefixes its older tickets use.

### Change

- `ContextConfig` in `src/chitty/config.py` gets `old_prefixes: list[str]`, default empty, each entry following the same rule as `prefix`. `RepoConfig`'s check that no prefix belongs to two contexts covers old prefixes too; an entry may not repeat or equal its own context's `prefix`.
- `Context` in `src/chitty/store.py` gets `old_prefixes: tuple[str, ...] = ()`, filled from the config in `Repo.context`. Contexts discovered from directories with no configuration (built with prefix `""`) keep the default.
- `docs/plan/config.md` describes the setting and how to restart numbering: on `main`, set `prefix` to the new prefix and add the old one to `old_prefixes`.

Nothing reads the field yet; the sibling tickets do.

### Out of scope

Reading or numbering old-prefix tickets (the sibling tickets).

## Acceptance Criteria

- [ ] In `tests/test_config.py`, configuration validation refuses an `old_prefixes` entry that does not match the `prefix` rule, that repeats within the list, that equals its own context's `prefix`, or that another context uses as its `prefix` or in its `old_prefixes`, each with an error naming the prefix; a valid `old_prefixes = ["TASK"]` loads, and `Repo.context(name).old_prefixes` returns `("TASK",)`. Fails without the change.

## History

- 2026-11-26T17:52:02Z calm-ochre-quail → cold-read
