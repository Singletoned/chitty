---
title: Record the chitty version in chitty.toml and warn when init needs re-running
status: todo
created: 2026-10-28
---

## Description

Repos set up by an older chitty keep stale setup (for example a managed guide block that says chitty pull) until someone re-runs chitty init, and nothing tells them to. init should record the chitty version that last set up the repo in chitty.toml, and every command should warn when that version is older than the running one, since init is idempotent and cheap to re-run. A recorded version newer than the running chitty means the install is out of date.

## Acceptance Criteria

- [ ] init writes and updates a version key in chitty.toml (e.g. chitty_version = "0.1.1") with the running package version
- [ ] Any command run against a repo whose recorded version is older, or missing, prints one warning on stderr to re-run chitty init; stdout and exit status are unaffected
- [ ] A recorded version newer than the running chitty prints a warning to upgrade chitty
- [ ] Re-running init clears the warning; config validation accepts the key
- [ ] Tests cover missing, older, equal and newer versions; PLAN.md and README describe the key

## Notes

Requested by the human. Possible refinement if the warning is noisy on every release: record a setup revision that only changes when init's output changes, instead of the package version.

## History

- 2026-10-28 → todo
