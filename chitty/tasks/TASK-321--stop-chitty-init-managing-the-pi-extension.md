---
title: Stop chitty init managing the Pi extension
status: cold-read
labels:
  - needs-minor
owner: planning
depends_on:
  - TASK-278
parent: TASK-275
created: 2026-11-13
---

## Description

Stop `chitty init` validating, installing or updating the Pi extension, or changing Pi settings via the `exposeSessionEnvironment` migration. Never inspect or modify existing extension files, `chitty-extension.sha256`, or Pi settings; preserve local edits. Keep the bundled extension for the subsequent removal ticket. Rewrite obsolete installer and settings-migration assertions in `tests/test_cli.py`, `tests/test_next.py`, and other affected tests. Document that existing installations may still autoload and users should inspect and remove them and their state file manually, then restart Pi. Do not change runner commands or remove the bundled extension in this ticket. Use Hypothesis to vary present and absent files, arbitrary file contents, and repeated fresh and existing-project init runs. Write tests first and record their failures before the fix.

## Acceptance Criteria

- [ ] Generated tests show repeated `chitty init` never creates or changes the installed extension or state file and never changes Pi settings, including `exposeSessionEnvironment`; tests fail against the current installer and migration.
- [ ] Documentation describes manual cleanup; `make check` passes without tests requiring Chitty to manage Pi extension files or settings.

## History

- 2026-11-13T22:24:27Z mellow-umber-lapwing → backlog
- 2026-11-13T22:24:50Z mellow-umber-lapwing: changed labels, dependencies, description, acceptance criteria
- 2026-11-13T22:24:50Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:25:23Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:25:23Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:26:25Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:26:25Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:32:40Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:32:40Z mellow-umber-lapwing planning → cold-read
