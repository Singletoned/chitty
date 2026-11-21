---
title: Say loudly when a `chitty run --loop` stops
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-20 both the work and review loops exited at 17:48 (one on a duplicate-ID error, one on a ticket parse error after a failed landing rebase). The only sign was the last lines in their terminals; an agent watching ticket status every 30 minutes did not notice, and the human found it by looking. A loop that stops should be impossible to miss: a desktop notification (macOS `osascript -e 'display notification ...'`), a line in the inbox, or a status file such as `.chitty/run-<mode>.status` that other tools and agents can watch. Better still, a per-ticket error should mark that ticket and let the loop continue, stopping only for errors that affect every ticket.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:58:07Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:08Z nimble-umber-gannet: changed notes
