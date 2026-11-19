---
title: Keep scratch roots out of the user inbox registry
status: backlog
created: 2026-11-19
---

## Description

Running `chitty init` (or other commands that register a root) in a throwaway folder registers it in the real inbox at `~/.local/share/chitty/inbox/<name>/repo`, unless `XDG_DATA_HOME` is set. On 2026-11-19 the inbox held about ten such entries from agent probes (`probe`, `probe2`, `probe3`, `rep`, `rep2`, `repro`, `proj`, `r`, `ac-probe`, `exitprobe`, `tmps0tf3zag`), each pointing at a scratch or temp folder, several of which no longer exist. Cold readers and planners probe Chitty behaviour in scratch roots often. Options: prune entries whose path no longer exists when the registry is read; or skip registration for roots under the system temporary directory; or both. Also take names from more than the folder basename, since `r` and `repo`-style names collide.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:34Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:35Z sunny-white-dormouse: changed notes
