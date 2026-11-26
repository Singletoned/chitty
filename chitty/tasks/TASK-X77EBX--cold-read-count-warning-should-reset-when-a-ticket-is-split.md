---
title: Cold-read count warning should reset when a ticket is split
status: backlog
created: 2026-11-26
provisional: true
---

## Description

In echonomicon on 2026-11-25, TASK-235 was cold-read once, then split (half moved to new TASK-239) and rewritten. Its next `chitty check` warned '3 cold reads; simplify or split instead of another read', although the split ticket had had only one read in its new shape. The count comes from History transitions into cold-read and never resets, so the warning fires on exactly the tickets the guide's advice ('split') produced. Suggestion: count only cold reads since the last title change, or since the last description replacement larger than some fraction, or let `chitty edit --reset-cold-reads` mark a split.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-26T10:54:47Z calm-ochre-quail → backlog
- 2026-11-26T10:54:50Z calm-ochre-quail: changed notes
