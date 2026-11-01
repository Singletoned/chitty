---
title: Show the ends of blocked-task chains
status: backlog
created: 2026-11-01
---

## Description

Add a view that shows, for each blocked task, the unblocked tasks at the end of its chain, following both `depends_on` and parent-to-child links (a parent waits on its open children). Today finding out why a task is blocked means `chitty show` on each task in turn, which is slow when blocks chain (A waits on B, B on C, C is in review). Something like `chitty list --blocked-by` or a `chitty blockers` command; it would also help to rank the end tasks by how many tasks each one unblocks, so the most valuable next action is obvious. It could also flag stale blocks: a `blocked` task whose dependencies are all done.

Example from circuitry on 2026-10-31, produced by a throwaway script over `chitty list --all --json`:

    CIRCUIT-67 Transition the public site to the catalogue design
        end:      CIRCUIT-78 [review] Rebuild the map from real Natural Earth coastline data
    CIRCUIT-80 Make location search the site's front door
        end:      CIRCUIT-82 [review] Filter nearby results by date and distance
    CIRCUIT-84 Design the search results page in the catalogue style
        end:      CIRCUIT-82 [review] Filter nearby results by date and distance

That showed at a glance that three blocked tasks came down to two reviews. Note that a task can be both a dependency and a child of the same parent (CIRCUIT-78 of CIRCUIT-67), so deduplicate.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
