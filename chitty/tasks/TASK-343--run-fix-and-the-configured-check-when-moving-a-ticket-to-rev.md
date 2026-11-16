---
title: Run fix and the configured check when moving a ticket to review
status: planning
created: 2026-11-16
---

## Description

`work.md` tells workers to run `chitty fix`, format and check before `-s review`. The runner already runs the check before a review session, so a forgotten check costs a whole session. Make `chitty edit -s review` run `chitty fix` and the configured check, and refuse on failure with the output. Then remove the instruction from the guide. Planning decides how this behaves where no check is configured.

## History

- 2026-11-16T09:59:52Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:34Z intrepid-coral-raven backlog → planning
