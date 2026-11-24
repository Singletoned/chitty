---
title: Work agents quit within seconds on freshly planned tickets, leaving them in error
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

Seen twice on 2026-11-23, both right after planning moved a ticket to `todo` and a cold read found nothing serious. TASK-629 (`tidy-teal-adder`, 19:01-19:06) and TASK-599 (`daring-hazel-eel`, 19:42-19:43) each ended in `error` with a runner note like: "last session: exit 0 after 11s / I have not completed TASK-599. It remains in `doing`; I cannot honestly classify it as ready for review, defective, or externally blocked." No code was changed and no planning blocker was named. In the same hour, TASK-358 (similar size) was worked and passed review normally. Worth checking: what the agent read in those 10 seconds (is the work prompt or `chitty guide work` telling it to stop when a ticket is large?), and whether the runner should retry once or name the agent session's last output. Both tickets are large (TASK-599 has 5 criteria and many cases), so "ticket too large" may be what the agent meant but did not say; if so, the work guide should make it say so and return to `planning`.

## Notes

Suggestion origin: chitty

Duplicate of TASK-562 (work agents stop early on larger tickets); the evidence is recorded there.

## History

- 2026-11-24T22:21:26Z zesty-coral-newt → backlog
- 2026-11-24T22:21:27Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:49Z zesty-coral-newt: changed labels, notes
