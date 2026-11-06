---
title: Shrink Chitty's block in `AGENTS.md`
status: doing
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

`chitty init` already replaces the block, so existing repositories pick this up through the version bump. Under `TASK-218` and `TASK-219`, a ticket branch must not change the managed block in `AGENTS.md` or run `chitty init`: leave the block exactly as on `main`, and the main checkout regenerates it after landing. Outside the block, in this repository's own section, replace the cold-read pointer with `chitty guide plan`, and drop anything the block no longer needs.

`main`'s `src/chitty/guide.md` has changed since this branch started (`TASK-217`, `TASK-219`). Rebase onto `main` and rewrite the short guide against `main`'s current text. Keep the sentence "On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`.", which a test checks for. Bump `__version__` one patch above `main`'s.

Out of scope: the rest of a repository's `AGENTS.md`, which Chitty does not own.

## Acceptance Criteria

- [x] `README.md` and `PLAN.md` describe where instructions live
- [x] `src/chitty/guide.md` is about ten lines and names `chitty guide <role>`, and every rule removed appears in the `TASK-141` accounting
- [ ] A test shows `chitty init` replacing the old long block in an existing repository with the new one
- [x] This repository's `AGENTS.md` managed block is identical to `main`'s, the cold-read line outside it names `chitty guide plan`, and `__version__` is one patch above `main`'s.

## Plan

Rebase onto main, retain main's managed AGENTS.md block unchanged, and rewrite src/chitty/guide.md from main's current concise role-pointer text. Bump only src/chitty/__init__.py to one patch above main, then run the focused guide/init tests and make format && make check. Verify the guide, version, and managed-block invariants before updating the ticket and handing off for review.

## Notes

Same cold read. Fixed: the blank line consumed before a following section, which would have failed the old criterion 2, confirmed by reading the code at `init_repo`; `re.subn` treating the guide as a template; and exactly one `## ` line. Rule accounting moved to `TASK-141`, which writes the role files. Rejected: an end marker for the block, because it adds format for every repository to protect text after the block that nobody has reported. Raised with the human as a question, since that text is replaced today.

Changed 2026-11-04: the human decided the block should have strict markers, in `TASK-144`. That replaces the blank-line, template and single-heading fixes this ticket had taken from its cold read, and the end-marker rejection in that note no longer stands.

Implemented the concise managed guide, refreshed this repository with updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/chitty.toml
updated /Users/singletoned/.local/share/chitty/inbox/chitty
updated /Users/singletoned/src/singletoned/chitty/.worktrees/task-143/AGENTS.md, and verified legacy-block replacement. The version is 0.1.39 because the version-bump check reported main at 0.1.38 despite the branch ref showing 0.1.37;  was left unchanged per repository instructions.

Correction: the prior note and summary lost literal backtick quoting because the shell expanded backticks; the implementation and verification claims remain unchanged.

Review failed (integration): rebasing onto `main` conflicts in `AGENTS.md`, `src/chitty/__init__.py`, `src/chitty/guide.md`.

Blocked by newer main policy: TASK-218 now requires ticket branches to leave the managed `AGENTS.md` block unchanged, while this ticket requires changing that block and running `chitty init` here. Rebasing onto `main` therefore conflicts in `AGENTS.md`, `src/chitty/guide.md`, and `src/chitty/__init__.py`, and preserving TASK-143 would undo the human decision in TASK-218. Human resolution needed: supersede TASK-218 policy for this migration, or close/redefine TASK-143 against the main-only init workflow. Verification also exposed that `make check` rejects the branch version as not above current main.

Unblocked and redefined by a human-run session. The branch's `AGENTS.md` block change and `chitty init` run are now forbidden (`TASK-218`, `TASK-219`), so the old criterion 1 was replaced: keep `main`'s block, and `main` regenerates it after landing. Criterion 3 is unchecked because the guide must be rewritten against `main`'s newer text. Next steps: rebase onto `main`; resolve `src/chitty/guide.md` by shortening `main`'s version; restore `AGENTS.md`'s block from `main`; bump `__version__`; run `make check`.

Rebased onto current main. Main advanced to 0.1.41 during the session, so __version__ is 0.1.42. Updated review-rebase regression setup to mutate the current concise managed-block text; the old test replacement was a stale assumption.

Review failed (tests): the migration regression test replaces a short hand-written block, not the old long managed guide from before TASK-143, so it does not demonstrate that chitty init replaces the legacy long block. Freeze the legacy guide text (or an equivalent full fixture) in the test and assert the concise block is installed while surrounding content remains.

1: pass - README.md and PLAN.md describe the role-guide location.
2: pass - The concise guide names all three role guides and TASK-141 accounts for removed rules.
3: fail - The test does not use the old long managed block.
4: pass - AGENTS.md matches main, the plan guide pointer is present, and version 0.1.42 is one patch above main 0.1.41.

## Summary

Handoff: src/chitty/guide.md is the concise role-pointer guide; AGENTS.md's managed block remains identical to main; README.md and PLAN.md document the role-guide split; init and review regression coverage is current; __version__ is 0.1.42. Verification: make format && make check passed (360 Python tests and Node tests), plus managed-block and 11-line guide invariants. Follow-ups: none.

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
- 2026-11-06T21:36:38Z youthful-toad: changed owner, description, acceptance criteria, notes
- 2026-11-06T21:36:38Z youthful-toad blocked → doing
- 2026-11-06T21:44:29Z brisk-quail: wrote the plan
- 2026-11-06T21:49:39Z brisk-quail: changed notes, summary; ticked acceptance criteria
- 2026-11-06T21:49:39Z brisk-quail doing → review
- 2026-11-06T21:53:39Z able-raven: changed acceptance criteria, notes
- 2026-11-06T21:53:39Z able-raven review → doing
