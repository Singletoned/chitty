---
title: Write `workflow = "runner"` when an upgrade would otherwise change a runner repository to tickets
status: doing
labels:
  - blocks-release
priority: high
depends_on:
  - TASK-415
parent: TASK-331
created: 2026-11-19
---

## Description

Upgrading a repository raises its recorded `chitty_version`, and a config with no `workflow` line resolves its workflow from that version (`resolve_workflow` in `src/chitty/config.py`; `TASK-415` sets the boundary: at most `0.5.0` is `runner`). So once the installed version is past the boundary, an upgrade silently turns a runner repository into a tickets one, hiding `chitty run` and `chitty next`. That is what release `0.5.0` did on 2026-11-19. The upgrade must write `workflow = "runner"` first. Split out of `TASK-331`, which keeps the rest (new repositories, `--workflow`).

Upgrades happen in `init_repo` in `src/chitty/store.py`: from `chitty init`, and from `Repo._prepare_write`, which runs `init_repo` before any write in an `autocommit` repository whose recorded version differs from the installed one and commits the result as `chitty: upgrade repository setup`.

Decisions:

- Add a pure function to `src/chitty/store.py`, beside the `_add_missing_*` helpers: `add_runner_workflow(text: str, recorded_version: str | None, pyproject: bool) -> str`. The Chitty section is the same span `_add_missing_settings` uses: the top level of `chitty.toml` before its first table header, or the `[tool.chitty]` table of `pyproject.toml` up to the next header. A key here means an uncommented line matching `^[ \t]*<key>[ \t]*=` (not `\s*`, which crosses blank lines under `re.M`); commented lines such as `# workflow = "tickets"` are not keys. When the section has no `workflow` key and `resolve_workflow(None, recorded_version)` is `"runner"`, it returns the text with one line `workflow = "runner"` inserted directly after the section's `chitty_version` line; otherwise it returns the text unchanged. When it must insert and the section has no `chitty_version` line, it raises `ChittyError` saying so. Keys named `workflow` or `chitty_version` outside the section (an `[agent_commands]` entry called `workflow`, a `[tool.other]` table) are ignored.
- `init_repo` calls it in the upgrade branch with the version recorded before the upgrade (`settings.get("chitty_version")`, `None` when absent), after `_add_missing_settings` (which adds a missing `chitty_version` line) and before the `re.sub` that rewrites `chitty_version`.
- Before writing the function, add it raising `NotImplementedError`, so the new tests fail on their own rather than at import.
- Out of scope, left in `TASK-331`: printing a line when the migration runs, new-repository configs, `--workflow`.

Tests, in a new `tests/test_init_workflow.py`, with Hypothesis, the repository's property-testing tool. Its classes inherit `RepoTestCase` (`tests/support.py`), which gives each test a temporary `XDG_DATA_HOME`.

- Generator for configs. The Chitty section is a drawn permutation of a drawn subset of these distinct lines (no key twice): `format = 1`, `default_context = "tasks"`, `autocommit = true`, `review = true`, `# a comment`, `# workflow = "tickets"`, `# chitty_version = "0.1.0"`, a blank line; plus the `chitty_version = <version>` line at a drawn position, and optionally a `workflow = "runner"` or `workflow = "tickets"` line at a drawn position. For `chitty.toml`, the section is followed by `[contexts.tasks]` with `prefix = "TASK"`, and optionally `[agent_commands]` with `workflow = "pi -p {prompt}"`. For `pyproject.toml`, the file starts with `[project]`, `name = "x"` and `chitty_version = "9.9.9"`, then `[tool.chitty]` and the section, then optionally `[tool.other]` with `workflow = "tickets"` and `chitty_version = "9.9.9"`; so a `chitty_version` or `workflow` key exists both before and after the section.
- Versions: the union of dot-separated integers (one to four parts, each from 0 to 6, so the `0.5` boundary is drawn often) and text drawn from `st.text(st.characters(max_codepoint=0xFFFF, exclude_characters="\x7f", exclude_categories=("Cs",)))`, written into the line with the default `json.dumps` (which `tomllib` reads back unchanged for that alphabet); add `@example`s `0.4.2`, `0.5.0`, `0.5.0.0`, `0.5.1`, `0.6` and `0.10.0`. `recorded_version` is the drawn version. The expected workflow comes from `resolve_workflow`, which `TASK-415` tests. The generator also returns `i`, the index in `text.splitlines()` of the whole file of the section's uncommented `chitty_version` line, because a decoy line can have the same text.
- Position check: when the line is added, the result's lines equal the input's lines with `workflow = "runner"` inserted at index `i + 1`, where `i` is the generator's index of the section's `chitty_version` line. Comparing only with the inserted line removed would pass an insert at the end of the section or after the `[project]` decoy.
- Direct cases, in the `chitty.toml` form (`pyproject=False`), for a section with no `chitty_version` line and no `workflow` line: with `recorded_version` `None` or `0.4.2` the function raises `ChittyError`; with `0.6.0` it returns the input unchanged. (From `init_repo` the raise cannot happen, because `_add_missing_settings` adds the line first.)
- The integration tests make real Git repositories: `git init -b main` in the test root, `user.name` and `user.email` configured, and the config committed. Build the config from `CONFIG` in `tests/support.py`, replacing `autocommit = false` with `autocommit = true`, removing the `workflow = "runner"` line and setting `chitty_version = "0.4.2"`, as `TestAutocommit.setUp` in `tests/test_autocommit.py` adjusts `CONFIG`. Set `CHITTY_ACTOR` for the CLI calls, as `CliTestCase.setUp` in `tests/test_cli.py` does; `RepoTestCase` removes it and `chitty add` fails without it. Run each integration test with the installed version patched to `0.5.1` (`mock.patch` of `CHITTY_VERSION` in both `chitty.store` and `chitty.config`), because with the installed `0.5.0` an upgrade still resolves to `runner` and the test could not fail before the change. Call `os.chdir(self.root)` in each integration test and restore the old directory with `addCleanup`, as `CliTestCase.setUp` does, because `chitty init` works on the current directory; invoke the CLI in-process with `CliRunner().invoke(cli, [...], catch_exceptions=False)`, since a subprocess would not see the patch. `chitty add` needs a description: `chitty add "<title>" --description "x"`.
- A prototype run by the cold read changed no existing test's expected output; edit an existing test only if it fails.

## Acceptance Criteria

- [ ] Property (Hypothesis), using the generator in Tests, for both file forms: when the section has no `workflow` key and the recorded version resolves to `runner`, the result passes the position check in Tests and `tomllib` reads `workflow` as `runner` in the Chitty section; otherwise the result equals the input. Applying the function twice equals applying it once. The direct no-`chitty_version` cases raise or return unchanged as Tests says
- [x] With the installed version patched to `0.5.1`, in the integration repository: `chitty init` leaves the exact line `workflow = "runner"` in the Chitty section; a second `chitty init` leaves `chitty.toml` and `AGENTS.md` byte for byte the same, and `AGENTS.md` still contains `chitty guide work`. In a second such repository, `chitty add` makes a `chitty: upgrade repository setup` commit (the commit before the add) whose `chitty.toml` has that line. Before the change, the line checks and the `AGENTS.md` check fail
- [x] `make check` passes

## Plan

Add section-aware add_runner_workflow with regression/property and integration coverage. First land a NotImplementedError stub and tests, confirm tests fail, then implement and wire migration into init_repo upgrade flow; format, run checks, and commit implementation with Task trailer.

## Notes

Review failed (tests): Newly discovered: implement the specified configuration generator and handle a final version line without a trailing newline.
1: fail - `tests/test_init_workflow.py` draws only versions and file form; it does not draw subsets or permutations, explicit workflow values, comments, blank lines, or optional decoy tables as required. Also `add_runner_workflow('chitty_version = "0.4.2"', '0.4.2', False)` printed `chitty_version = "0.4.2"workflow = "runner"\n`; `tomllib.loads` raised `TOMLDecodeError`. Insert a separating newline and add regression coverage.
2: pass - `make check` passed the integration tests. With migration patched to return the input unchanged, both integration tests failed their line checks; separately two `init` calls exited 0 and printed guide present `True`, then `False`, confirming the guide regression.
3: pass - `make check` exited 0: ruff, pyright, and 700 tests passed.

Review found the property generator does not exercise the specified section permutations, optional keys/comments, or decoy tables. It also exposed invalid TOML when the version line ends at EOF without a newline. I will expand the generator and fix the insertion boundary.

Review failed (tests): Newly discovered: add the six specified explicit Hypothesis `@example` cases, rather than relying on sampled values that are not guaranteed to run.
1: fail - `tests/test_init_workflow.py` uses `st.sampled_from` for the six boundary versions but has no `@example` decorators, so the required deterministic cases are missing. The previous review generator and EOF findings are resolved; `make check` passes, and replacing the helper with `NotImplementedError` produced three test errors, including the property.
2: pass - `make check` ran both integration tests successfully. The previous review demonstrated both line checks fail with migration disabled and the guide check changes from `True` to `False` after the second init.
3: pass - `make check` exited 0: ruff, pyright and 701 tests passed.

## Summary

Expanded Hypothesis config generation to cover permuted Chitty-section lines, workflow/comment variants, and out-of-section decoys. Fixed EOF insertion to separate TOML lines. Verified focused workflow tests and make check (701 tests, lint, typecheck; full command completed successfully).

## History

- 2026-11-19T10:50:03Z quick-ginger-lapwing → planning
- 2026-11-19T10:50:14Z quick-ginger-lapwing: changed description
- 2026-11-19T10:50:19Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T10:57:58Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T10:57:58Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T10:58:21Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:01:34Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:01:34Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:01:38Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:05:36Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:05:38Z quick-ginger-lapwing: changed description
- 2026-11-19T11:05:38Z quick-ginger-lapwing planning → todo
- 2026-11-19T11:06:03Z youthful-ochre-vole todo → doing
- 2026-11-19T11:06:53Z youthful-ochre-vole: wrote the plan
- 2026-11-19T11:10:35Z youthful-ochre-vole: changed summary
- 2026-11-19T11:10:37Z youthful-ochre-vole: ticked acceptance criteria
- 2026-11-19T11:10:40Z youthful-ochre-vole doing → review
- 2026-11-19T11:13:46Z youthful-bronze-crane: changed acceptance criteria, notes
- 2026-11-19T11:13:46Z youthful-bronze-crane review → doing
- 2026-11-19T11:19:43Z calm-amber-eel: changed notes
- 2026-11-19T11:22:42Z calm-amber-eel: changed summary
- 2026-11-19T11:22:42Z calm-amber-eel doing → review
- 2026-11-19T11:25:14Z eager-violet-marten: changed acceptance criteria, notes
- 2026-11-19T11:25:14Z eager-violet-marten review → doing
