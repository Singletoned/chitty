---
title: Refuse two -file options that both read stdin in one chitty edit
status: backlog
created: 2026-11-23
---

## Description

In one call, `chitty edit TASK-568 --note-file - --summary-file /dev/stdin -s review <<'EOF'` stored the whole heredoc as the note and an empty Summary, with no warning. Refuse, with a clear error, when more than one --\*-file option reads stdin ('-' or /dev/stdin), so that a section is never left empty without anyone noticing.

## Notes

Suggestion origin: chitty

## History

- 2026-11-23T10:24:06Z witty-russet-gannet → backlog
- 2026-11-23T10:24:07Z witty-russet-gannet: changed notes
