---
title: Accept native Pi identity without an extension warning
status: cold-read
owner: planning
parent: TASK-275
created: 2026-11-13
---

## Description

The warning in `src/chitty/actor.py` and `src/chitty/cli.py` says Pi needs the Chitty extension even when native `PI_SESSION_ID` supplies an identity. Align the warning with `actor()` and give an actionable `CHITTY_ACTOR` remedy when identity is missing. Keep existing actor precedence and do not change the extension or runner. Use Hypothesis to generate nonempty and whitespace-only identity values for `PI_SESSION_ID`, `CHITTY_PI_SESSION_ID`, and `CHITTY_ACTOR` in Pi and non-Pi environments. Write regression tests first and record failures before the fix.

## Acceptance Criteria

- [ ] Generated tests show native `PI_SESSION_ID` suppresses the warning, whitespace-only identities do not, and a genuinely missing Pi identity gets a warning that does not require the extension; the native ID test fails before the fix.

## History

- 2026-11-13T22:24:26Z mellow-umber-lapwing → backlog
- 2026-11-13T22:24:49Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-13T22:24:49Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:25:07Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:25:07Z mellow-umber-lapwing planning → cold-read
