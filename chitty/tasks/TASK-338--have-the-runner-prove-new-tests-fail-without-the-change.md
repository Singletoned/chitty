---
title: Have the runner prove new tests fail without the change
status: backlog
created: 2026-11-16
---

## Description

Replaces the cold read implementing pass and the guide rule, repeated in every role guide, that a worker must show a regression test fails without the fix. Missing or weak tests are the main review failure cause (31 `Review failed (tests)` here, 69 in echonomicon). Before review, the runner runs the tests added or changed on the branch against the branch merge base with non-test changes removed, and requires at least one to fail. Design decisions for planning: how to identify the new tests per repository language, and what to do for tickets with no code change.

## History

- 2026-11-16T09:50:19Z intrepid-coral-raven → backlog
