---
title: Retire the Chitty Pi extension
status: planning
labels:
  - needs-minor
owner: planning
depends_on:
  - TASK-278
parent: TASK-275
created: 2026-11-11
---

## Description

Retire the Chitty Pi extension: `chitty run` already passes the guide using `{prompt}`, continues unfinished sessions, and exports `CHITTY_ACTOR`. Preserve that shared actor for runner descendants. Interactive Pi sessions outside `chitty run` need not share an identity with their subagents; Pi's native `PI_SESSION_ID` remains supported. Remove the extension's interactive commands, startup flags and usage-file writer without replacements.

Stop `chitty init` installing or updating the extension and remove the bundled extension and its tests. Do not automatically delete or overwrite existing installed copies or user Pi settings: these may contain user edits. Document that an old copy can still autoload and that users must inspect and remove it themselves, migrate extension-based agent commands to a `{prompt}` command, and restart Pi. Update setup guidance, generated configuration examples, warnings and current documentation to stop requiring or recommending the extension. A missing-identity warning must not claim the plugin is required; `PI_SESSION_ID` is a valid identity.

Do not edit `chitty.toml` on a ticket branch. Its local `pi-tui` command needs a separate human-owned main-checkout migration. Preserve unrelated Node tooling, including Prettier. Historical tickets need not be rewritten.

Use Hypothesis for properties. Test first and record failure without the change. For installation, generate existing extension file contents and presence/absence across repeated `chitty init` runs and assert the installed file is never created or changed. Cover both fresh and previously initialised projects. For identity, generate Pi environments with and without `PI_SESSION_ID` and `CHITTY_ACTOR`, and test the warning and actor selection. Runner identity protection needs a fake agent and child process: prove the child inherits the runner actor; do not start a real agent session.

## Acceptance Criteria

- [ ] Generated fresh and repeat `chitty init` tests prove no extension is created or an existing copy changed; they fail against the current installer. The bundled extension and extension-only tests are removed.
- [ ] Generated Pi identity tests prove `PI_SESSION_ID` is accepted without an extension warning, missing identity gets an actionable warning, and a fake runner agent and its child inherit the same `CHITTY_ACTOR`. The warning regression fails before the change.
- [ ] Current setup guidance, generated examples and documentation use `{prompt}` rather than extension commands and explain the manual migration and removal of existing installed copies. The removed interactive commands, flags and usage-file writer have no replacement.

## History

- 2026-11-11T13:21:35Z vivid-yellowhammer → backlog
- 2026-11-13T22:14:12Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:14:12Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:14:35Z mellow-umber-lapwing: changed title, description, acceptance criteria
