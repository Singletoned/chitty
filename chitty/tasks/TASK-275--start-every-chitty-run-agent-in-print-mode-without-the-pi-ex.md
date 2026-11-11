---
title: Start every `chitty run` agent in print mode, without the Pi extension
status: backlog
created: 2026-11-11
---

## Description

- Decided with the human on 2026-11-10 and 2026-11-11: work, review and cold-read all start the agent the same way, as a plain command with the guide as `{prompt}`. Use plugins only for what must be in one.
- Pi and `claude` run in print mode. `chitty run` does not know where session files are; usage is a separate analysis of the session files.
- The `pi-print` trial in `chitty.toml` (TASK-243) worked, but showed only the final message and warned `cannot read usage file`.
- The children carry the work, smallest first.

## History

- 2026-11-11T13:21:31Z vivid-yellowhammer → backlog
