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

The human decided on 2026-11-04 that the global `chitty` is the latest PyPI release, and that a person is told when to upgrade. `make release` writes the version to `$XDG_DATA_HOME/chitty/pending-release` (`TASK-80`). This ticket acts on that file. `TASK-161` adds checking for people who did not make the release.

Put the logic in a new `src/chitty/upgrade.py`, and call it from `main()` in `src/chitty/cli.py` in a `finally` around `cli()`. Click ends `cli()` by raising `SystemExit` even on success, so plain code after it never runs. The `finally` also covers failed commands and keeps their exit code. Skip it when `_CHITTY_COMPLETE` is set, so a TAB press stays quiet. Tests that use `CliRunner` never reach `main()`, so they cannot reach the network.

An editable install does nothing at all: no request, no alert, no change to the file. It is running a checkout, not a release, so `direct_url.json` from `importlib.metadata.distribution("chitty")` saying `dir_info.editable` is the test. This repository's `.venv` and the worktrees' are editable, so the alert appears when the global `chitty` runs, in other repositories, and agents developing Chitty never see it. The person making a release already knows about it.

For any other install, when `pending-release` exists:

1. If the running version has reached it, delete the file and stop.
2. If its second line is `out`, print the alert and stop, with no request.
3. If the file's modification time is under `UPGRADE_RETRY_SECONDS` old, a module constant of 60, stop. Otherwise touch it and ask `PYPI_URL`, a module constant of `https://pypi.org/pypi/chitty/json`, for `info.version`, using `urllib` with a 2-second timeout. Without this limit, a failed publish or no network would add up to 2 seconds to every command.
4. If that version has reached the pending one, add the `out` line and print the alert.

The alert goes to stderr: `chitty <version> is out: run uv tool upgrade chitty`. Nothing goes to stdout. Compare with `_version_key`, wherever it then lives.

A failed request or an unreadable file must not affect the command: it stays silent, because this is advice around someone else's work, and comment that where it is caught.

Out of scope: upgrading automatically, and any setting to turn this off.

## Acceptance Criteria

- [ ] Tests against a local HTTP server, with `PYPI_URL` and the running version patched and calling `main()`, show no alert before the version is out, then one on stderr with exit code and stdout unchanged, no further request, and the file removed once the running version reaches it
- [ ] Tests show a failed request and an unreadable file changing nothing, no second request within `UPGRADE_RETRY_SECONDS`, the alert after a failing command, and an editable install doing nothing
- [ ] `README.md` describes the alert

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: `main()` needs a `finally`, because Click always raises `SystemExit`; completion; where `out` is recorded; and a limit on requests, since an offline machine would otherwise wait on every command. Dropped my editable rule: `uv tool list` reports 0.1.19 for today's editable global, so it could have alerted forever, and it needed `uv` on every command. An editable install now does nothing, so a person working only in this repository sees no alert. Moved the invocation count to `TASK-161`. Rejected: pre-release and yanked versions, which `info.version` already handles; an empty `XDG_DATA_HOME`, which `inbox_path` has too; a non-editable install from a local path, which is rare and harmless.

## History

- 2026-11-04T19:32:38Z mellow-newt → backlog
- 2026-11-04T19:36:37Z mellow-newt: changed description, acceptance criteria, notes
