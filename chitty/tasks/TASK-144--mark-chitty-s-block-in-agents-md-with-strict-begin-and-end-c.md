---
title: Mark Chitty's block in `AGENTS.md` with strict begin and end comments
status: doing
priority: medium
parent: TASK-140
created: 2026-11-04
---

## Description

`chitty init` finds its block in `AGENTS.md` with a pattern: from `## Chitty` to the next `## ` heading or the end of the file. It cannot know where its own text stops, so unheaded text a person adds after the block is deleted, the blank line before a following section is lost, and a second `## ` line in the guide would leave part of the old block behind. Decided by the human on 2026-11-04: `chitty init` should know exactly what it replaces.

Wrap the block in `AGENTS.md` in strict comments, which also say it was inserted by Chitty:

```markdown
<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->

## Chitty

...

<!-- chitty:end -->
```

In `init_repo` in `src/chitty/store.py`, replace exactly the text from the begin line to the end line, and nothing around it, using plain string slicing rather than `re.subn`, which treats the guide as a template. A marker counts only as a whole line equal to the expected text. Keep the blank lines shown: checked on 2026-11-04, `prettier` adds one after the begin comment and `mdformat` also adds one before the end comment, so without them a formatter and `chitty init` would keep rewriting each other's output. `src/chitty/guide.md` itself has no markers: `chitty guide` and `chitty://guide` print the same text as now, and `init_repo` adds them.

- Exactly one begin line followed by one end line: replace between them.
- No markers and no `## Chitty` line: append the block, as now.
- Anything else with markers (one without the other, reversed, or more than one pair): fail with a message naming `AGENTS.md`, and write nothing, saying to remove the marker lines so the next `chitty init` can migrate the block. A person must repair it, because Chitty no longer knows what is its own. An older `chitty init` run on a marked file causes this, since it replaces from `## Chitty` to the end of the file and drops the end marker. Markers in a code fence count too, which at worst gives this same loud failure.

Use a distinct error type for this. `chitty init` and `chitty run` fail with it. `_prepare_write` in `src/chitty/store.py` must not: it runs `init_repo` before every write while the recorded version is stale, so a damaged marker would otherwise stop every write in the repository until repaired. There it warns on stderr, skips the upgrade so it is retried next time, and lets the write go ahead.
- No markers but a `## Chitty` line, which is every existing repository: migrate once by using the old pattern to find the block, then writing it with markers. Comparing against known versions instead would mean shipping a record of all 26 versions of `guide.md` in Git, and the human preferred markers. The change goes through Git, so it can be seen and undone. Keep the blank line before a following section, and report the migration on stderr. As with any migration, unheaded text after an old block is replaced this once.

Bump `__version__`, so existing repositories upgrade. This repository's `AGENTS.md` then upgrades through `chitty init` in the main checkout after landing, so do not edit its block by hand on the branch.

`src/chitty/import_backlog.py` also looks for `## Chitty`: check it still does the right thing with a marked block.

Out of scope: CRLF, because `read_text` and `write_text` already normalise a whole file to LF today; the guide's content, which is `TASK-143`, and `chitty.toml`.

## Acceptance Criteria

- [x] Tests show a new `AGENTS.md`, and one with content but no block, getting the block with both markers, and `chitty guide` printing no markers
- [x] Tests show an old block migrated to markers with a following section keeping its heading and blank line, and a message on stderr
- [x] `README.md` and `PLAN.md` describe the markers, and `__version__` is bumped above `main`'s
- [x] Tests show a marked block replaced with text before and after it unchanged, including unheaded text after it and a guide containing a backslash, a second `chitty init` changing nothing, and `prettier` leaving the result unchanged
- [x] Tests show a begin with no end, an end with no begin, reversed markers and two pairs each failing `chitty init` with a message naming `AGENTS.md`, with the file unchanged, and a stale repository in that state warning on a write, with the write succeeding and the version not advanced

## Plan

1. Inspect init_repo, _prepare_write, import_backlog, existing tests, README.md, and versioning.
2. Implement strict marker parsing, migration, distinct error handling, and stale-upgrade warning behavior without changing guide output.
3. Add focused unittest coverage for creation, migration, replacement/idempotence, malformed markers, and stale writes; update README.md and PLAN.md and bump version.
4. Run focused tests, then make format and make check; inspect the final diff and commit with Task: TASK-144.

## Notes

Cold read by a fresh Sonnet subagent with `TASK-145`, 2026-11-04. Fixed: a damaged marker stopping every write through `_prepare_write`, the most serious finding; the repair path, including an older `chitty init` causing the damage; and "byte for byte", which overstated it because `read_text` normalises line endings. Found by testing its question: `prettier` and `mdformat` both changed my marker layout, so the block now has blank lines they leave alone. Rejected: a guard in old code, which cannot be added to versions already out there. A `## Chitty` line in a code fence triggering migration, and a hand-edited `## chitty` heading getting a second block, because both are rare, visible in Git and already happen today. `AGENTS.md` being a symlink, because `write_text` follows it. A regular-file `CLAUDE.md`, which already fails earlier in `init_repo`. An explicit test for an absent `AGENTS.md`, which criterion 2 already covers.

Review failed (integration): rebasing onto `main` conflicts in `chitty.toml`.

Rebased onto `main` by a human-run session to unstick the branch. `main`'s `chitty` had upgraded this branch's `chitty.toml` to config this branch's code couldn't read (`TASK-204`). Conflicts resolved:
- `chitty.toml` keeps `main`'s `chitty_version = "0.1.33"`.
- `__version__` is now `0.1.34`, one patch above `main`, because this branch changes the managed block. If `TASK-203` (also `0.1.34`) lands first, bump again.
- `src/chitty/errors.py` and `store.py` keep both `NoNextTicket` and `ManagedGuideError`.
- `tests/test_pi_extension.py` compares against `__version__` rather than a literal.
`make check` passes (310 tests). The next Chitty write here will record `0.1.34` in `chitty.toml`; after that, `main`'s `chitty` (`0.1.33`) refuses writes in this worktree until it lands. Re-check each criterion against the rebased code.

## Summary

Implemented strict AGENTS.md markers, legacy migration, exact marked-block replacement, malformed-marker errors, and stale-write warning behavior. Updated README.md, PLAN.md, and bumped __version__. Re-verified all five criteria; focused init tests pass (29 tests), full Python suite passes (310 tests), ruff and pyright pass. Follow-up: any repository with malformed markers requires manual marker removal.

## History

- 2026-11-04T12:31:58Z lively-panda → todo
- 2026-11-04T12:34:33Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-05T21:47:42Z intrepid-eel todo → doing
- 2026-11-05T21:47:58Z intrepid-eel: wrote the plan
- 2026-11-05T22:03:46Z intrepid-eel: ticked acceptance criteria
- 2026-11-05T22:03:47Z intrepid-eel: ticked acceptance criteria
- 2026-11-05T22:03:48Z intrepid-eel: ticked acceptance criteria
- 2026-11-05T22:03:49Z intrepid-eel: ticked acceptance criteria
- 2026-11-05T22:03:50Z intrepid-eel: ticked acceptance criteria
- 2026-11-05T22:03:51Z intrepid-eel: changed summary
- 2026-11-05T22:03:58Z intrepid-eel doing → review
- 2026-11-06T10:05:49Z upbeat-otter: changed notes
- 2026-11-06T10:05:49Z upbeat-otter review → doing
- 2026-11-06T12:53:55Z youthful-toad: changed notes
- 2026-11-06T14:47:05Z daring-eel: changed summary
