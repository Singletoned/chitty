---
title: chitty run with the pi extension flag exits 0 doing nothing when there is no TTY
status: backlog
created: 2026-11-19
---

## Description

Evidence from echonomicon on 2026-11-19 09:17-09:30: seven work tickets (TASK-156, 157, 159, 160, 161, 163, 164) went to `error` with "was unchanged; only committed changes are visible to `chitty run`". `~/.local/share/chitty/usage/echonomicon.jsonl` shows each agent phase took about 2 seconds, and each ticket pi session folder under `~/.pi/agent/sessions/` is empty. Echonomicon uses `agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"`. The extension only starts a ticket inside `session_start` when `ctx.mode === "tui"`; otherwise it does nothing and pi exits 0. Reproduced: `pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-work TASK-9999 </dev/null` exits 0 after 1s with no output and leaves an empty session folder. Startup errors inside `startSafely` also end in a clean `ctx.shutdown()` with exit 0, and the runner keeps no agent output, so the ticket note gives no cause. Suggestions: (1) when `--chitty-work` or `--chitty-review` is set and the mode is not tui, or startup fails, exit non-zero with the reason on stderr; (2) have `chitty run` refuse to start a non-`{prompt}` agent command without a TTY, or record the agent stderr tail in the runner error note; (3) consider making the extension path work in print mode, as the chitty repo itself uses `pi -p ... {prompt}`.

## Notes

Suggestion origin: echonomicon

Archived: the Chitty part (record why the agent ended, via a per-session log named in the error note) is folded into `TASK-276`. The extension at `~/.pi/agent/extensions/chitty.ts` is a local copy outside this repository; the bundled extension was retired in `TASK-279`, so the fix there is to move echonomicon to a `{prompt}` print-mode `agent_command`.

## History

- 2026-11-19T20:55:16Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:17Z sunny-white-dormouse: changed notes
- 2026-11-19T21:13:01Z sunny-white-dormouse: changed notes
