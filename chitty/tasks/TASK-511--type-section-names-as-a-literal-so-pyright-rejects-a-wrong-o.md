---
title: Type section names as a `Literal`, so pyright rejects a wrong one
status: cold-read
parent: TASK-376
created: 2026-11-21
---

## Description

On 2026-11-21 a planner wrote a property using invented section names, which `parse` rejects as `unknown section`. `Task.section(name: str)` and `Task.with_section(name: str, text: str)` (`src/chitty/model.py`) accept any string, so nothing flagged it.

Decisions:

- In `src/chitty/model.py`, add `SectionName = Literal["Description", "Acceptance Criteria", "Plan", "Notes", "Summary", "History"]`. Annotate `DESCRIPTION`, `ACCEPTANCE_CRITERIA`, `PLAN`, `NOTES`, `SUMMARY` and `HISTORY` as `Final[SectionName]`, and `SECTION_ORDER` as `tuple[SectionName, ...]`.
- `Task.section` and `Task.with_section` take `name: SectionName`. Their runtime checks stay as they are.
- Callers that pass a name only known at run time (check each with pyright; on 2026-11-21 these were in `src/chitty/check.py`, `cli.py`, `import_backlog.py` and `inbox.py`) either pass one of the constants, or iterate `SECTION_ORDER` or another tuple typed `tuple[SectionName, ...]`. Where a name truly comes from outside (user input or a file), convert it with a new `section_name(text: str) -> SectionName` in `model.py`, which raises `TaskError("unknown section: <text>")` for anything else. Do not use `cast`.
- No behaviour change.

Tests: a new `tests/test_section_name_types.py`. One test writes a small Python file in a temporary directory that imports `chitty.model` and calls `parse(...).with_section("Bogus", "x")`, runs `.venv/bin/pyright` on it (`subprocess.run`, `cwd` the repository root, so the project configuration applies), and asserts a non-zero exit with `"Bogus"` in the output. A second test does the same with `"Notes"` and asserts exit 0. A third checks that `section_name` returns each name in `SECTION_ORDER` unchanged and raises `TaskError` for `"Bogus"`. Before the change, the first test fails, because pyright accepts any `str` (record this in a note).

## Acceptance Criteria

- [ ] The `"Bogus"` pyright test fails before the change and passes after (recorded in a note); the `"Notes"` test and the `section_name` test pass
- [ ] `grep -n "def section\|def with_section" src/chitty/model.py` shows `name: SectionName` for both; no `cast` is added; `make check` passes

## History

- 2026-11-21T14:32:29Z sunny-ebony-kestrel → planning
- 2026-11-21T14:32:31Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T14:32:31Z sunny-ebony-kestrel planning → cold-read
