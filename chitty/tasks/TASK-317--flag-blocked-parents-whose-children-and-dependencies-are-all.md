---
title: Flag blocked parents whose children and dependencies are all done
status: backlog
created: 2026-11-13
---

## Description

In circuitry, parents CIRCUIT-67 and CIRCUIT-80 stayed `blocked` after every child (and every depends_on, e.g. HUMAN-4) reached `done`. Their notes said "blocked until CIRCUIT-84 is done", but nothing moved them on, so they sat idle until a human asked why. Suggest that `chitty list`, `chitty next` or `chitty check` reports blocked tasks whose children and dependencies are all done, or that completing the last child moves the parent to `review` automatically.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-13T14:02:38Z zesty-umber-puffin → backlog
- 2026-11-13T14:02:39Z zesty-umber-puffin: changed notes
