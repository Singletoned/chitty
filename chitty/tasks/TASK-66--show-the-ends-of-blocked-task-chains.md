---
title: Show the ends of blocked-task chains
status: backlog
depends_on:
  - TASK-70
created: 2026-11-01
---

## Description

Add a view that shows, for each blocked or waiting task, the workable tasks at the end of its chain, following `depends_on` links. Today finding out why a task is held up means `chitty show` on each task in turn, which is slow when chains are long (A waits on B, B on C, C is in review). Something like `chitty list --blocked-by` or a `chitty blockers` command; it would also help to rank the end tasks by how many tasks each one frees, so the most valuable next action is obvious. Stale blocks are handled by TASK-70.

Example from circuitry on 2026-10-31, produced by a throwaway script over `chitty list --all --json`:

    CIRCUIT-67 Transition the public site to the catalogue design
        end:      CIRCUIT-78 [review] Rebuild the map from real Natural Earth coastline data
    CIRCUIT-80 Make location search the site's front door
        end:      CIRCUIT-82 [review] Filter nearby results by date and distance
    CIRCUIT-84 Design the search results page in the catalogue style
        end:      CIRCUIT-82 [review] Filter nearby results by date and distance

That showed at a glance that three held-up tasks came down to two reviews. Deduplicate end tasks reached by more than one path.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
