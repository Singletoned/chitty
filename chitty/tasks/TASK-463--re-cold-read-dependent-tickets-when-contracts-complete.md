---
title: Re-cold-read dependent tickets when contracts complete
status: backlog
created: 2026-11-19
---

## Description

Add a dependency-transition gate for tickets that depend on architecture or specification work. Keep the child blocked until the dependency is done; when it completes, mark the child as requiring a fresh cold read against the dependency output before it can enter todo or doing. Evidence: TASK-1 was cold-read while ARCHITECTURE.md was absent, then implemented after that contract changed without a final cold read; missing malformed URL-port cases were discovered only through three review failures. This would make contract changes trigger the required re-validation instead of relying on planner memory.

## Notes

Suggestion origin: injustice-league

## History

- 2026-11-19T20:55:40Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:41Z sunny-white-dormouse: changed notes
