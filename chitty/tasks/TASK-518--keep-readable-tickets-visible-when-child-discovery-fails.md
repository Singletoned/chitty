---
title: Keep readable tickets visible when child discovery fails
status: planning
parent: TASK-480
created: 2026-11-21
---

## Description

Change only `chitty show` and its child discovery (`src/chitty/cli.py`, narrow store helper in `src/chitty/store.py`). Do not change listing semantics (`TASK-480`) or write paths. Use the source selection already landed in `TASK-378`, not `all_tasks()` or `git.historical_files`.

Resolve the requested ticket normally with `find`; any error for it remains fatal. JSON never looks for children and keeps exactly the existing shape (no `children` key). Plain show keeps the children line: enumerate IDs with `ticket_ids()`, resolve each other ticket independently, and include the authoritative tickets in configured contexts whose structured parent parses to the selected ID using `TaskId.parse`, preserving configured-context order and then ID order. For a candidate whose source selection or body parsing raises `ChittyError`, continue with other candidates and warn on stderr that the children list may be incomplete. Include that candidate ID and the original error. If its source is known to be in an unconfigured directory, skip it without parsing. Do not catch arbitrary exceptions, and do not weaken errors in the initial selected-ticket lookup. Keep other show output unchanged.

In a new `tests/test_show_authoritative_children.py` use `CliTestCase` and the Git helpers from `tests/test_source_copy_errors.py`. Real Git is needed to exercise divergent copies and bindings to CLI surfaces; the source policy has property tests in `tests/test_property_ticket_source.py`. Use fresh repos or subtests with reset state. Assert regression failures on unchanged code before implementing, then pass the new tests and `make check`.

Fixture: on main commit a readable parent `TASK-2`, a readable `TASK-3` with `parent: TASK-2`, and valid `TASK-1`. Change the parent title to `branch parent` on `task-2`, commit, return to main and spoil only the main working-tree copy of `TASK-2` with `not frontmatter`. Run all criteria against two fresh variants. In variant A independently change `TASK-1` on main and `task-1` (do this before spoiling `TASK-2`). In variant B leave the committed main `TASK-1` valid and commit a malformed `TASK-1` body on `task-1` only. In both variants the unreadable candidate is `TASK-1`. Validate the fixture by asserting `Repo.find(TASK-2)` selects `task-2` and `Repo.find(TASK-1)` raises the expected conflict or parse error. The `children` line must be exactly `children: TASK-3`; the warning names `TASK-1` and reflects the corresponding error, and must not report the non-authoritative malformed `TASK-2` body.

## Acceptance Criteria

- [ ] In each of the two fixture variants, plain `show` exits 0, prints the selected authoritative title and the valid child ID, and warns on stderr with `TASK-1` and the variant-specific error.
- [ ] In the same fixtures `show --json` exits 0 with the selected authoritative title, no `children` key and no warning. Assert no source resolution or body parsing for any other ticket, using a test-local probe on the Repo source resolver that raises if it receives any other ID.
- [ ] Selecting the unreadable candidate itself fails with its own error in both plain and JSON mode; the selected ticket failure must not be downgraded to a child warning.

## Notes

Planning: The specified fixture has only one configured context and one child, so it cannot verify configured-context then ID ordering. It also has no unconfigured-directory source, so it cannot verify skipping that source before body parsing, and uses only the canonical parent spelling, so it cannot distinguish structured `TaskId.parse` comparison from the existing string comparison in `src/chitty/cli.py`. Please specify fixtures, actions and assertions for these required behaviors, including an unconfigured malformed source and a parent spelling that parses to the selected ID. The existing two variants and JSON resolver probe cover the remaining stated criteria; source selection and parsing are exposed by `Repo._source_files` and `Repo._parse_source_copy`. Implementation and regression verification were not started because the required tests are unspecified.

Return to planning: required regression fixtures are missing; see the preceding planning note for evidence and requested decisions.

## History

- 2026-11-21T18:38:33Z eager-ginger-adder → backlog
- 2026-11-21T18:42:31Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:42:31Z eager-ginger-adder backlog → cold-read
- 2026-11-21T18:43:17Z eager-ginger-adder cold-read → planning
- 2026-11-21T18:43:19Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:43:19Z eager-ginger-adder planning → cold-read
- 2026-11-21T18:45:09Z eager-ginger-adder cold-read → planning
- 2026-11-21T18:45:10Z eager-ginger-adder planning → todo
- 2026-11-21T18:48:55Z plucky-ginger-urchin todo → doing
- 2026-11-21T18:51:22Z plucky-ginger-urchin: changed notes
- 2026-11-21T18:51:26Z plucky-ginger-urchin: changed owner, notes
- 2026-11-21T18:51:26Z plucky-ginger-urchin doing → planning
