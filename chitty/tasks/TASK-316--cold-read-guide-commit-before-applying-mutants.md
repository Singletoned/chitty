---
title: "Cold-read guide: commit before applying mutants"
status: backlog
created: 2026-11-13
---

## Description

In echonomicon on 2026-11-12, a cold reader (TASK-146) restored a mutant with `git checkout -- src`, which also threw away its uncommitted implementation of the ticket; it had to reapply the edits. `chitty guide cold-read` says to apply each mutant and restore it, but not how. Suggest the guide says: commit the implementation before applying any mutant, then restore each mutant with `git checkout HEAD -- <file>` or `git diff | git apply -R`, never a bare `git checkout -- <dir>` over uncommitted work.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-13T14:02:37Z zesty-umber-puffin → backlog
- 2026-11-13T14:02:38Z zesty-umber-puffin: changed notes
