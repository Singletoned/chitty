---
title: Shrink Chitty's block in `AGENTS.md`
status: blocked
priority: medium
depends_on:
  - TASK-142
  - TASK-144
parent: TASK-140
created: 2026-11-04
---

## Description

Third of three parts of `TASK-140`. `AGENTS.md` belongs to the repository, so reduce Chitty's block there to what every session needs, now that each role has its own instructions.

Rewrite `src/chitty/guide.md` to about ten lines: tasks live in `chitty/`; use the CLI or MCP and do not hand-edit task files; backticks for paths and code; `chitty --help` for commands; and which `chitty guide <role>` to run, for a person who starts an agent by hand, keeping the pointer to `chitty guide plan` from `TASK-187`. `TASK-141` has already given every other rule a home and accounted for them in a note: check that against the final text.

`chitty init` already replaces the block, so existing repositories pick this up through the version bump. `TASK-144` makes that replacement exact. Run it here so this repository's `AGENTS.md` matches. In this repository's own section, replace the cold-read pointer with `chitty guide plan`, and drop anything the block no longer needs.

Out of scope: the rest of a repository's `AGENTS.md`, which Chitty does not own.

## Acceptance Criteria

- [x] This repository's `AGENTS.md` matches and its cold-read line names `chitty guide plan`, and `__version__` is bumped above `main`'s
- [x] `README.md` and `PLAN.md` describe where instructions live
- [x] `src/chitty/guide.md` is about ten lines and names `chitty guide <role>`, and every rule removed appears in the `TASK-141` accounting
- [x] A test shows `chitty init` replacing the old long block in an existing repository with the new one

## Plan

Update the managed guide template and this repository's instructions to the concise role-oriented block, preserving the strict-marker format. Bump the package patch version, add or adjust the init regression coverage for replacing legacy blocks, update README/PLAN instruction pointers, then run formatting and the full check suite.

## Notes

Same cold read. Fixed: the blank line consumed before a following section, which would have failed the old criterion 2, confirmed by reading the code at `init_repo`; `re.subn` treating the guide as a template; and exactly one `## ` line. Rule accounting moved to `TASK-141`, which writes the role files. Rejected: an end marker for the block, because it adds format for every repository to protect text after the block that nobody has reported. Raised with the human as a question, since that text is replaced today.

Changed 2026-11-04: the human decided the block should have strict markers, in `TASK-144`. That replaces the blank-line, template and single-heading fixes this ticket had taken from its cold read, and the end-marker rejection in that note no longer stands.

Implemented the concise managed guide, refreshed this repository with updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty.toml
updated /Users/singletoned/.local/share/chitty/inbox/chitty
updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/AGENTS.md, and verified legacy-block replacement. The version is 0.1.39 because the version-bump check reported main at 0.1.38 despite the branch ref showing 0.1.37;  was left unchanged per repository instructions.

Correction: the prior note and summary lost literal backtick quoting because the shell expanded backticks; the implementation and verification claims remain unchanged.

Review failed (integration): rebasing onto `main` conflicts in `AGENTS.md`, `src/chitty/__init__.py`, `src/chitty/guide.md`.

Blocked by newer main policy: TASK-218 now requires ticket branches to leave the managed `AGENTS.md` block unchanged, while this ticket requires changing that block and running `chitty init` here. Rebasing onto `main` therefore conflicts in `AGENTS.md`, `src/chitty/guide.md`, and `src/chitty/__init__.py`, and preserving TASK-143 would undo the human decision in TASK-218. Human resolution needed: supersede TASK-218 policy for this migration, or close/redefine TASK-143 against the main-only init workflow. Verification also exposed that `make check` rejects the branch version as not above current main.

## Summary

Handoff: src/chitty/guide.md now contains the concise pointer block; AGENTS.md, README.md, and PLAN.md document the role-guide split; init regression coverage verifies replacing a legacy block; version bumped to 0.1.39. Verification: focused init/guide tests, make format, make check, chitty fix, and chitty check (warnings only for pre-existing ticket Markdown).

## History

- 2026-11-04T11:56:20Z lively-panda → todo
- 2026-11-04T12:00:40Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T12:32:19Z lively-panda: changed dependencies, description, acceptance criteria, notes
- 2026-11-05T14:23:17Z mellow-newt: changed description
- 2026-11-06T20:15:30Z open-urchin todo → doing
- 2026-11-06T20:15:48Z open-urchin: wrote the plan
- 2026-11-06T20:22:51Z open-urchin: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:22:51Z open-urchin doing → review
- 2026-11-06T20:23:03Z open-urchin: changed notes, summary
- 2026-11-06T20:24:15Z sunny-crane: changed notes
- 2026-11-06T20:24:15Z sunny-crane review → doing
- 2026-11-06T20:30:01Z rosy-kestrel: changed notes
- 2026-11-06T20:30:01Z rosy-kestrel doing → blocked
