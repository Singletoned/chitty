---
title: Squash a planning session's consecutive edits to one ticket
status: backlog
created: 2026-11-23
---

## Description

Each `chitty edit` makes its own commit. In echonomicon on 2026-11-22, planning TASK-172 (moving it planning -> cold-read -> planning -> todo across three cold reads) produced about 10 commits like `chitty: edit TASK-172 ...` in a row. Status moves cost a commit each, since the guide requires them. Consider amending the previous commit when it is a chitty commit for the same ticket by the same actor and not yet pushed, or offer a batch mode, so `git log` stays readable.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-23T10:24:09Z witty-russet-gannet → backlog
- 2026-11-23T10:24:10Z witty-russet-gannet: changed notes
