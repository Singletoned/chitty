---
title: Refuse ticket branches that change `AGENTS.md`'s managed block
status: doing
priority: high
depends_on:
  - TASK-212
created: 2026-11-06
---

## Description

Only `chitty init` on the main checkout writes Chitty's managed block in `AGENTS.md` (the human's decision, 2026-11-06), just as only it writes `chitty.toml` (`TASK-212`). In the same `_prepare_review` check in `src/chitty/run.py` that `TASK-212` adds, fail the ticket if the branch changes the managed block compared with `main`. Use the note `Review failed (work): the branch changes Chitty's managed block in `AGENTS.md`; only `chitty init` on the main checkout may change it. Restore that block from `main`.`.

- **The block.** It is the text from the `GUIDE_BEGIN` line to the `GUIDE_END` line (`src/chitty/store.py`). A file without markers uses the legacy `## Chitty` section. Factor the lookup out of `_managed_agents` into a public `managed_block`, so both use one function. Read file contents at a ref with a new `git.file_at(root, ref, path)`.
- **Allowed.** Edits to the rest of `AGENTS.md` are allowed.
- **Edge cases.**
  - Broken markers on the branch count as a change.
  - `AGENTS.md`, or its block, present on only one side counts as a change.
  - Absent on both sides is no change.
  - A rebase conflict in `AGENTS.md` already fails as `integration`.
- **Tests.** `chitty run` refreshes `AGENTS.md` on the main checkout before the rebase, so a test fixture's block must be the real `guide()` text, or the rebase conflicts for the wrong reason. Assert the exact note. Test the legacy-section lookup through `managed_block` directly.
- **This repository.** A branch that changes `src/chitty/guide.md` leaves `AGENTS.md` alone; the main checkout's setup refresh regenerates it after landing. `task-179` and `task-181` edit the block today and must restore it before they can pass.

Out of scope: `CLAUDE.md`, which is a symlink here.

## Acceptance Criteria

- [ ] Tests show a branch that edits inside the managed block failing review with that note and no agent run, and a branch that edits only outside it passing.
- [ ] A unit test of `managed_block` covers marked and legacy files, and `_managed_agents` uses it with its behaviour unchanged (existing `init` tests pass).

## History

- 2026-11-06T18:13:06Z youthful-toad → backlog
- 2026-11-06T18:13:30Z youthful-toad backlog → todo
- 2026-11-06T20:03:40Z eager-crane todo → doing
