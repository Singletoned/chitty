---
title: Re-sample planned tickets for property tests after TASK-302
status: backlog
owner: human
depends_on:
  - TASK-302
created: 2026-11-12
---

## Description

- Baseline (2026-11-12): in a random sample of 15 tickets finished before TASK-302, 11 could have had a property test and one (TASK-270) did; 3 had a valid reason for none (TASK-217 docs, TASK-238 a small fixed set, TASK-246 real processes).
- Once about 15 tickets planned after TASK-302 lands are done, sample them the same way: for each, did it specify properties or give a valid one-line reason, did the worker use a generating tool, and did a review or later bug find a missed property.
- Planning-session work, not a worker ticket. Record the counts in a note and compare with the baseline; suggest guide changes if the rate has not moved.

## History

- 2026-11-12T20:18:42Z kind-yellow-vole → backlog
