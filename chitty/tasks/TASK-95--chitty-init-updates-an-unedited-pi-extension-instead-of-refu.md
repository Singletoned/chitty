---
title: "`chitty init` updates an unedited Pi extension instead of refusing"
status: todo
priority: high
created: 2026-11-01
---

## Description

TASK-93's guard in `install_pi_extension` refuses whenever the installed `chitty.ts` differs from the current shipped file. Every change to the extension therefore makes `chitty init` fail on every machine, including copies Chitty itself installed and nobody edited. With TASK-82, a version bump also blocks writes until `init` succeeds, so every repo gets stuck until someone deletes the file by hand. Seen on 2026-11-01 after the 0.1.12 bump (TASK-94). Also, `init` wrote `chitty_version = "0.1.12"` to `chitty.toml` before failing and never refreshed the guide block in `AGENTS.md`, so the repo claims to be current when it isn't.

## Acceptance Criteria

- [ ] `chitty init` replaces an installed extension that Chitty installed and nobody has changed since (for example, by recording the hash it wrote), with a test
- [ ] It still fails loudly, naming the file, when the installed extension has local edits
- [ ] A failing `chitty init` leaves `chitty.toml` and the guide block unchanged: checks run before any write, with a test

## History

- 2026-11-01 → todo
