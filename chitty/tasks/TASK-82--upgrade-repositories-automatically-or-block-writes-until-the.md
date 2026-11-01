---
title: Upgrade repositories automatically, or block writes until they are upgraded
status: backlog
priority: high
created: 2026-11-01
---

## Description

Format and setup changes are applied by two commands, `init` (guide, config) and `fix` (file repairs), and nothing says when to run them. A strict reader also rejects files the moment a newer format arrives. Decided with the human (2026-11-01): either Chitty upgrades a stale repository itself, or it blocks every write until it is upgraded. Proposal: `init` is the single upgrade path and also runs format migrations. When the repository's `chitty_version` is older than the running Chitty, a write with `autocommit = true` first upgrades and commits that as its own commit, then does the write. With autocommit off, writes fail with 'run `chitty init`', so upgrade changes are never mixed into someone's uncommitted work. Reads always work. A Chitty older than the repository's `chitty_version` refuses clearly ('needs Chitty X or later') rather than failing validation. This replaces the 'no Chitty-format migrations in v1' principle in `PLAN.md`, and must land before format changes such as TASK-70 and TASK-74.

## Acceptance Criteria

- [ ] `chitty init` applies setup and format migrations, idempotently
- [ ] With `autocommit = true`, the first write in a stale repository upgrades it in a separate commit before the write
- [ ] With autocommit off, writes in a stale repository fail and say to run `chitty init`; reads still work
- [ ] Running a Chitty older than the repository's `chitty_version` fails with the version needed
- [ ] `PLAN.md` replaces the no-migrations principle and the init/fix split is documented

## History

- 2026-11-01 → backlog
