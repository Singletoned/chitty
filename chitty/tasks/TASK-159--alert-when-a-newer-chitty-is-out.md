---
title: Alert when a newer Chitty is out
status: backlog
priority: high
depends_on:
  - TASK-80
parent: TASK-106
created: 2026-11-04
---

## Description

The human decided on 2026-11-04 that the global `chitty` is the latest PyPI release, and that a person is told when to upgrade.

At the end of each command, in `main()` in `src/chitty/cli.py`, so also after a failed command and never before the work, and keeping its exit code, call a new `src/chitty/upgrade.py`. State lives under `$XDG_DATA_HOME/chitty/`, defaulting like `inbox_path`:

- `pending-release` holds a version a release is expected to reach. `make release` writes it (`TASK-80`). While it exists and the running version is older, each command asks PyPI for the latest version, using `urllib` with a 2-second timeout. Once PyPI has it, print on stderr `chitty <version> is out: run uv tool upgrade chitty`, on every command until upgraded, recording that it is out so later commands make no request. When the running version reaches it, delete the file.
- With no `pending-release`, count invocations in a file. Every `UPGRADE_CHECK_INTERVAL` invocations, a module constant of 100, ask PyPI, and if it is newer than the running version, write that version to `pending-release`. This is how other people find out, by the same path.

A request or state-file failure must not affect the command. It stays silent, because this is advice printed around someone else's work, and tries again next time; comment that where it is caught. Nothing goes to stdout, so `--json` stays valid.

An editable install is running code from a checkout, not a release. This repository's `.venv` is one, and would otherwise delete `pending-release` before the global install had upgraded. So an editable install, detected from the distribution's `direct_url.json`, does not count or delete, and compares against the version `uv tool list` reports for `chitty` instead of its own.

Out of scope: upgrading automatically, and any setting to turn this off.

## Acceptance Criteria

- [ ] Tests against a local HTTP server show `pending-release` causing a request and no alert until the version is out, then an alert on stderr with the exit code and stdout unchanged and no further request, and the file removed once the running version reaches it
- [ ] Tests show the 100th invocation with no `pending-release` asking PyPI and alerting when it is newer, and earlier ones making no request, and a failed request changing nothing
- [ ] A test shows an editable install leaving `pending-release` in place, and `README.md` describes the alert

## History

- 2026-11-04T19:32:38Z mellow-newt → backlog
