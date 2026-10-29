---
title: Allocate ticket IDs only on main; sub-tasks found on branches go through the inbox
status: backlog
parent: TASK-58
created: 2026-10-29
---

## Description

Branches that `chitty add` independently collide on the next ID, and `git.deleted_paths` only sees committed deletions, so history scanning cannot close the gap. Rule: a sub-task finished on the branch is an acceptance criterion or note; one done separately is sent with `chitty suggest . "title" --task TASK-<n>` and numbered when pulled on main. `pull` currently ignores the suggestion `task:` field; it should set the new ticket's `parent` from it. Replace the "creation is assumed centralised" paragraph in PLAN.md and update the guide. Open question: whether `chitty add` should refuse, or warn, off the main branch.

## History

- 2026-10-29 → backlog
