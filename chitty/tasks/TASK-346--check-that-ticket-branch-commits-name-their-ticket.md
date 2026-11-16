---
title: Check that ticket branch commits name their ticket
status: planning
created: 2026-11-16
---

## Description

`work.md` tells workers to end implementation commits with `Task: <ID>`. Check it mechanically at `-s review`: list branch commits since the merge base, other than Chitty autocommits, that lack the trailer, and refuse. Then shorten the guide text to the one-line convention.

## History

- 2026-11-16T09:59:56Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:39Z intrepid-coral-raven backlog → planning
