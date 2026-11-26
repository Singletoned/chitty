---
title: Add an `old_prefixes` setting to contexts
status: todo
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

- `ContextConfig` in `src/chitty/config.py` gets `old_prefixes: list[str] = []`, each entry checked by the same rule as `prefix` (a field validator over the list, reusing `PREFIX_RE`). `RepoConfig`'s check that no prefix belongs to two contexts builds one list of every context's `prefix` and `old_prefixes`, so any prefix appearing twice (in two contexts, twice in one list, or as both a context's `prefix` and one of its `old_prefixes`) is refused. Each error message contains the prefix.
- `Context` in `src/chitty/store.py` gets `old_prefixes: tuple[str, ...] = ()`, filled from the config in `Repo.context`. Contexts discovered from directories with no configuration (built with prefix `""`) keep the default.
- `docs/plan/config.md` describes the setting and how to restart numbering: on `main`, set `prefix` to the new prefix and add the old one to `old_prefixes`.

Nothing reads the field yet; the sibling tickets do.

### Out of scope

Reading or numbering old-prefix tickets (the sibling tickets).

## Acceptance Criteria

- [ ] In `tests/test_config.py`, a Hypothesis property test (`@settings(max_examples=examples(N))`) writes a `chitty.toml` (the `test_rejections` pattern: write it, then `load_repo_config(self.root)`) with two contexts whose `prefix` and `old_prefixes` are drawn from a small set of prefixes, sometimes with an entry that breaks `PREFIX_RE`. Loading is refused, with a message containing the offending prefix, exactly when some entry breaks the rule or some prefix appears more than once across both contexts' `prefix` and `old_prefixes`; otherwise it loads. Fails without the change, because `old_prefixes` is an unknown key today.
- [ ] With `old_prefixes = ["TASK"]` on the `tasks` context and `prefix = "TK"`, `Repo.context("tasks").old_prefixes` returns `("TASK",)`. Fails without the change. `make check` passes.

## History

- 2026-11-26T17:52:02Z calm-ochre-quail → cold-read
- 2026-11-26T17:53:12Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T17:53:12Z calm-ochre-quail cold-read → todo
