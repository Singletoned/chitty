---
title: Keep the section-name type test's probe file out of the Git work tree
status: doing
labels:
  - bug
created: 2026-11-22
---

## Description

`tests/test_section_name_types.py` writes a probe file in `tempfile.TemporaryDirectory(dir=ROOT)`, where `ROOT` is the repository root, so pyright reads the project configuration. While the test runs, the directory (for example `tmpt1qelkfu/example.py`) is an untracked file in the checkout, and any `git add -A` at that moment stages it. Seen 2026-11-22 in the `task-550` worktree: the staged `tmpt1qelkfu/example.py` failed `make check` (Ruff format) and blocked the ticket.

Fix: create the temporary directory under the repository's ignored `tmp/` directory instead (`(ROOT / "tmp").mkdir(exist_ok=True)`, then `tempfile.TemporaryDirectory(dir=ROOT / "tmp")`). Confirm `tmp/` is in `.gitignore` and that pyright still applies the project configuration there (the test's assertions on `Bogus` and `Notes` must keep passing). Evidence: while the test runs, `git status --porcelain --untracked-files=all` shows nothing new (for example, run it from inside a patched `subprocess.run` in a temporary test, or by inspection of the path), and the two existing tests still pass.

## Acceptance Criteria

- [ ] The probe directory is created under `tmp/`, which is ignored; the existing tests in `tests/test_section_name_types.py` pass; `make check` passes

## Plan

Create the probe under ignored tmp/, verify the ignore rule and existing type tests, then run make check and commit.

## Summary

Moved type test probes under ignored tmp/. Verified git check-ignore, all four section-name tests, and make check.

## History

- 2026-11-22T05:15:59Z lively-zinc-newt → todo
- 2026-11-22T05:23:03Z golden-teal-marten todo → doing
- 2026-11-22T05:25:48Z golden-teal-marten: wrote the plan
- 2026-11-22T05:28:29Z golden-teal-marten: changed summary
