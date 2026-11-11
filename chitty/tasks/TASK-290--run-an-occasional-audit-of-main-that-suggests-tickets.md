---
title: Run an occasional audit of `main` that suggests tickets
status: backlog
created: 2026-11-11
---

## Description

- An occasional pass on `main`, run by hand, turns security and test-quality findings into suggestions in this repository's inbox, for the planner to triage.
- Scanners live in taidy (`taidy security`, suggested 2026-11-11). `make audit` (TASK-291) turns its findings into suggestions, skipping any whose title is already a ticket.
- Mutation testing is a separate `make mutate`, run overnight (TASK-295).

## History

- 2026-11-11T16:18:07Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:46Z vivid-yellowhammer: changed description
- 2026-11-11T18:50:47Z vivid-yellowhammer: changed description
- 2026-11-11T18:50:48Z vivid-yellowhammer: changed notes
- 2026-11-11T18:50:55Z vivid-yellowhammer: changed title
- 2026-11-11T18:59:41Z vivid-yellowhammer: replaced notes; changed description
