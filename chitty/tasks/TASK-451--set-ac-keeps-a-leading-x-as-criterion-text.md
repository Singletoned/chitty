---
title: "`--set-ac` keeps a leading `[x]` as criterion text"
status: backlog
created: 2026-11-19
---

## Description

On 2026-11-19 `chitty edit TASK-401 --set-ac 2 "[x] text"` stored the criterion as `2. [ ] [x] text`, and `--check 2` then showed `[x] [x] text`. Once a ticket is in `review`, `--set-ac` is refused and leaving `review` needs a verdict note, so the doubled tick cannot be removed. `--set-ac` (and `--ac`) should reject text starting with `[ ]` or `[x]`, or treat it as the tick state.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:25Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:27Z sunny-white-dormouse: changed notes
