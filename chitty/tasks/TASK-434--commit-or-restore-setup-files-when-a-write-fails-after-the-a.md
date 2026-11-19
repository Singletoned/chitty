---
title: Commit or restore setup files when a write fails after the automatic upgrade
status: backlog
created: 2026-11-19
---

## Description

In an autocommit repository, `Repo._prepare_write` runs `init_repo` before a write and commits `chitty: upgrade repository setup`. If the write then fails before that commit, the rewritten `chitty.toml` is left modified and uncommitted. Seen 2026-11-19 while smoke-testing an upgrade from 0.5.0 to 0.6.0 on a clone of echonomicon: `chitty add` failed with `project echonomicon is registered to <other path>; choose explicit project = name`, and `git status` then showed ` M chitty.toml` (chitty_version 0.6.0 and a new workflow line). `TASK-388` restores ticket files after a failed write but not the setup files the upgrade touched. Either commit the upgrade before validating the write, or restore the setup files on failure.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:05Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:06Z sunny-white-dormouse: changed notes
