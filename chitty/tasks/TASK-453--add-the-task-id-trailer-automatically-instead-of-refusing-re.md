---
title: "Add the `Task: <ID>` trailer automatically instead of refusing review without it"
status: backlog
created: 2026-11-19
---

## Description

Since `TASK-346` (commit `b43aa534`, 2026-11-17), `Repo.edit` in `src/chitty/store.py` refuses `-s review` when a non-`chitty:` commit on the branch (`git rev-list --no-merges main..HEAD`) has no `Task: <ID>` line in its last paragraph (`git.commits_missing_trailer`). Agents keep tripping on it, because the only instruction is one line in `src/chitty/roles/work.md`. Any agent that did not load that guide misses it: a human-directed session, a repair, or an agent fixing a blocked ticket. It happened on 2026-11-19 when an agent fixed `TASK-403` by hand, and the user reports seeing other agents complain about it. The error appears only at the end and suggests `git rebase -i`, which agent harnesses usually cannot run because it is interactive. Proposal: move the step to tooling. When Chitty creates or reuses a ticket worktree, install a `prepare-commit-msg` hook (or set `commit.template` per worktree) that appends `Task: <ID>` when the branch is a ticket branch and the trailer is absent. Keep the review check as a backstop, and change its message to a non-interactive fix, such as `git commit --amend` for the last commit or a `git rebase --exec` command that adds the trailer to each listed commit.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:28Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:29Z sunny-white-dormouse: changed notes
