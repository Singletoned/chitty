---
title: "`chitty edit -s review` runs the check silently and looks hung"
status: backlog
created: 2026-11-22
---

## Description

Seen 2026-11-22: the owner ran `chitty edit TASK-540 -s review --human` in the main checkout and reported it "just hangs forever". `Repo.edit` (`src/chitty/store.py` around line 986) runs the configured `check` (`make check`, about 3 minutes here) on entering `review`, with all output going to `.chitty/check.log` and nothing on the terminal. A planner session hit the same thing moving `TASK-569` to `review` (the shell tool timed out at 120 s). Suggest printing one line to stderr before the check starts, for example `running check `make check` before review (output in .chitty/check.log)...`, and the elapsed time when it ends. Also worth deciding: whether moving to `review` should run the check at all when the ticket has no branch and its work is already on `main` (as for `TASK-540`), since it then checks unrelated code in the main checkout.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T13:16:27Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:27Z friendly-jade-stoat: changed notes
