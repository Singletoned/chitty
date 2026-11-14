---
title: Add a workflow setting, tickets by default
status: planning
labels:
  - needs-minor
priority: medium
created: 2026-11-14
---

## Description

Chitty was meant to be a plain ticketing system; the runner pipeline (worktrees, review, landing, role guides) is a layer on top. Add a `workflow` setting that chooses between them, with `tickets` as the default.

- `workflow` in `chitty.toml` or `[tool.chitty]`: `"tickets"` or `"runner"`. Missing means `"runner"` when `chitty_version` is missing or older than `FIRST_WORKFLOW_VERSION` (a module constant, `"0.5.0"`; the `needs-minor` label makes this ticket's release `0.5.0`), and `"tickets"` otherwise. Every older config was set up for the runner, so it keeps its behaviour. Any other value is a config error naming the key and both allowed values.
- `review` defaults to `false` under `tickets` and `true` under `runner`. An explicit repository `review` still wins, and a context's `review` still overrides the repository's.
- This deliberately changes the rule in `docs/plan/config.md` that new defaults keep existing behaviour: a repository set up by `0.5.0` or later with no `workflow` key gets `tickets`. Record that decision there, and record in `docs/plan/direction.md` that tickets-only is Chitty's original purpose and the runner is an optional layer. Later tickets migrate existing runner repositories through `chitty init`.
- This ticket changes only the setting and the `review` default; `chitty init`, the managed block, and which commands and guides are visible are separate tickets.

## Acceptance Criteria

- [ ] With no `workflow` key, the loaded workflow is `runner` when `chitty_version` is missing or older than `0.5.0`, and `tickets` when it is `0.5.0` or later; `"runner"` and `"tickets"` load as written whatever the version; any other value fails with an error naming `workflow` and both allowed values.
- [ ] With no repository `review` key, the repository default is `false` under `tickets` and `true` under `runner`; an explicit `review` wins under either workflow, and a context `review` still overrides the repository value.
- [ ] `docs/plan/config.md` documents `workflow` and the changed-default decision; `docs/plan/direction.md` records that tickets-only is the original purpose.
- [ ] Tests through the config loader cover criteria 1 and 2, and fail without the change.

## Notes

Replanned with the human on 2026-11-14. The original ask (agents feel they must write tickets for a weaker agent and cannot review their own) is solved by a tickets-only workflow chosen at install time, not by an exploratory agent mode. Stages: this ticket (setting), then `chitty init` with migration, then the managed block, hidden runner commands and hidden role guides. Earlier cold-read questions about `chitty run` invocation no longer apply.

## History

- 2026-11-14T13:39:35Z jolly-umber-badger → planning
- 2026-11-14T13:40:56Z jolly-umber-badger: changed notes
- 2026-11-14T18:21:52Z friendly-ginger-adder: replaced notes; changed title, labels, description, acceptance criteria
- 2026-11-14T18:23:25Z friendly-ginger-adder: changed description, acceptance criteria
