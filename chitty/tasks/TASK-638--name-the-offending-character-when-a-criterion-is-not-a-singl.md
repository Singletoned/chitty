---
title: Name the offending character when a criterion is not a single line
status: backlog
created: 2026-11-23
---

## Description

On 2026-11-23, `chitty edit TASK-610 --set-ac 1 ...` was refused with only `Error: acceptance criterion must be a single line`. The text had no newline; it contained a Unicode line separator character (U+2028), which `splitlines()` treats as a line break. It took a guess to find it. Say which criterion (number or first words) and name the character and its position, for example `criterion 1 contains U+2028 LINE SEPARATOR at column 212`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-23T11:57:37Z witty-russet-gannet → backlog
- 2026-11-23T11:57:41Z witty-russet-gannet: changed notes
