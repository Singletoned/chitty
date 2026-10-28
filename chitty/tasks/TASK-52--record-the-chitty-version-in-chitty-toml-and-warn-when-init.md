---
title: Record the chitty version in chitty.toml and warn when init needs re-running
status: review
created: 2026-10-28
---

## Description

Repos set up by an older chitty keep stale setup (for example a managed guide block that says chitty pull) until someone re-runs chitty init, and nothing tells them to. init should record the chitty version that last set up the repo in chitty.toml, and every command should warn when that version is older than the running one, since init is idempotent and cheap to re-run. A recorded version newer than the running chitty means the install is out of date.

## Acceptance Criteria

- [x] init writes and updates a version key in chitty.toml (e.g. chitty_version = "0.1.1") with the running package version
- [x] Any command run against a repo whose recorded version is older, or missing, prints one warning on stderr to re-run chitty init; stdout and exit status are unaffected
- [x] A recorded version newer than the running chitty prints a warning to upgrade chitty
- [x] Re-running init clears the warning; config validation accepts the key
- [x] Tests cover missing, older, equal and newer versions; PLAN.md and README describe the key

## Plan

Inspect package-version loading, repository configuration parsing, command entry points and init upgrades; add the recorded setup version and non-failing stale/newer-version warnings without changing command output; cover all version states and document the key; then run make check.

## Notes

Requested by the human. Possible refinement if the warning is noisy on every release: record a setup revision that only changes when init's output changes, instead of the package version.

## Summary

Added `chitty_version` setup metadata, automatic upgrade by `init`, and non-failing stale/newer setup warnings. Covered missing, older, equal, newer, and refresh states; updated README and PLAN.md. Verified with `make check`.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
