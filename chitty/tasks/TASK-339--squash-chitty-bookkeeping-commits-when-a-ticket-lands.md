---
title: Squash Chitty bookkeeping commits when a ticket lands
status: planning
created: 2026-11-16
---

## Description

In the 14 days to 2026-11-16, 2392 of 2870 commits were `chitty: ...` autocommits. When `chitty run` lands a passing review, collapse the branch `chitty:` commits into one commit before fast-forwarding `main`, keeping implementation commits as they are. The ticket file already records its own history, so nothing is lost.

## History

- 2026-11-16T09:50:21Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:29Z intrepid-coral-raven backlog → planning
