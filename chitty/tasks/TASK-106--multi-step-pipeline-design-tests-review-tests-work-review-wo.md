---
title: "Multi-step pipeline: design, tests, review-tests, work, review-work"
status: backlog
priority: high
created: 2026-11-02
---

## Description

Replace the `todo`/`doing`/`review` flow with a multi-step pipeline, so design is done by a strong model with the human, and cheap models write tests and do the work as separate agents:

`backlog` → `design` → `tests` → `review-tests` → `work` → `review-work` → `done`

Unit tests written by the worker after the fact encode what the code does, not what it should do. Tests written from the design, by a different agent, before the implementation, are an independent check, and the worker's job is to make them pass without editing them.

Decisions with the human (2026-11-02):

1. Each stage is one status meaning "in this step". Claiming is recorded separately (for example `owner` or a History entry), not by a second status per stage, so two cheap agents cannot take the same ticket.
2. Status names, like all text identifiers, use hyphens (`review-tests`, `review-work`). The History format only accepts `[a-z-]`.
3. The human signs off at the end of `design`; that transition is human-only. Tests are checked by random sampling. For the first few tickets the human reviews each stage by hand before triggering the next, and good models do every stage so the finished tickets serve as examples (label them, e.g. `example`, so prompts can point at them).
4. A failed `review-tests` returns to `tests`, a failed `review-work` to `work`, each counting failures separately. When `work` or `review-work` finds that the design or tests are wrong, it blocks the ticket for a human; it never edits the spec tests.
5. Stages are configured generically in `chitty.toml`, replacing `review = true`, so more stages can be added. A ticket can skip stages with a recorded reason, e.g. `skip-stages = tests,review-tests` for prompt or docs changes.
6. Independence generalises: no actor reviews a stage it did, and the test writer does not do `work`. This extends the existing History-based review-independence check.
7. Each stage gets its own agent mode and model choice. The Pi `/chitty` extension gains one mode per stage; a Claude Code equivalent follows (it has the stronger models; see `TASK-89`).

Needs a design session with the human, in a clean context, before promotion. Likely absorbs or reshapes `TASK-65`, `TASK-70`, `TASK-71`, `TASK-74`, `TASK-76`, `TASK-88`, `TASK-91` and `TASK-78`.

## History

- 2026-11-02T17:11:36Z lively-otter → backlog
