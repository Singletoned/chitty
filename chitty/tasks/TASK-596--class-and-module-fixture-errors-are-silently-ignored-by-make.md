---
title: Class and module fixture errors are silently ignored by `make check` and `make test`
status: backlog
labels:
  - bug
depends_on:
  - TASK-597
created: 2026-11-22
---

## Description

Found by a cold read of `TASK-590`, 2026-11-22, and reproduced: `make check` and `make test` run `unittest-parallel` with `--level test` (`Makefile` lines 18 and 21). At that level a `setUpClass` that raises is never reported: a module with `setUpClass` raising `RuntimeError` and one passing `test_ok` gives `Ran 1 test` and `OK`, and the test runs without its class setup. With `--level class` or `--level module` the same module gives `FAILED (errors=1)`. The same holds for `setUpModule`; tear-down failures are presumably dropped too (not yet checked).

The suite has no `setUpClass`, `tearDownClass`, `setUpModule` or `tearDownModule` today (`grep` of `tests/`), so nothing is hidden yet; the first one added would fail silently.

Options to decide while planning: run at `--level class` (tests in a class then run serially, so check the effect on wall time with the timing history from `TASK-591`), or keep `--level test` and add a test that fails if any test module defines a class or module fixture. Once decided, the timing recorder (`TASK-590`, which leaves fixtures out of scope) may need to record fixture failures.

## History

- 2026-11-22T18:44:25Z plucky-umber-wren → backlog
- 2026-11-22T20:16:13Z plucky-umber-wren: changed dependencies
