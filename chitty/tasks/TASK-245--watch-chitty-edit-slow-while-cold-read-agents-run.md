---
title: "Watch: `chitty edit` slow while cold-read agents run"
status: backlog
priority: low
owner: human
created: 2026-11-10
---

## Description

Waiting to see whether this happens again. Do not implement yet; when it recurs, add a note with where and how, then decide.

First seen in mullion (2026-11-09): with five cold-read agents running in worktrees, one batch of `chitty edit` and `chitty note` calls took over two minutes; single calls were usually quick. Undiagnosed; possibly lock or autocommit contention with the readers' `git` commands.

## History

- 2026-11-10T14:08:45Z jolly-heron → backlog
