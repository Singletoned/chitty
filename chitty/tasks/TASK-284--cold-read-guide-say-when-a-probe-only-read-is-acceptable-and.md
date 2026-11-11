---
title: "Cold-read guide: say when a probe-only read is acceptable and give readers the mutant list"
status: backlog
created: 2026-11-11
---

## Description

Observation from planning TASK-82, TASK-98, TASK-113 and TASK-114 in echonomicon with Haiku cold readers (2026-11-11).

1. Readers often probe instead of implementing even though `chitty guide cold-read` says to implement. Two first-round readers stopped after probing. A probe-only first read is fine when it finds serious problems, because the ticket will change anyway. But a probe-only read that reports nothing serious should not count as clean: only an implementing read whose tests failed first can show the ticket is ready. The guide could say this explicitly, both to readers (implement unless you have found blocking problems) and to planners (do not promote on a clean probe).

2. The planning guide tells planners to use a fixed list of mutants for every read, but the cold-read guide does not mention mutants, so readers only apply them if the planner remembers to put them in the prompt. When they were given, they caught real gaps: in TASK-82 read 3, a worker holding `episode.lock` around `download_episode` survived because no criterion required the lock to be free. Suggest the cold-read guide include a section on applying the planner's mutants one at a time and reporting survivors with criterion wording that would catch them.

3. Minor: `chitty edit` keeps only the last of several `--replace-in-description` options, silently. Either apply all of them or reject repeats.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-11T16:08:27Z vivid-yellowhammer → backlog
- 2026-11-11T16:08:28Z vivid-yellowhammer: changed notes
