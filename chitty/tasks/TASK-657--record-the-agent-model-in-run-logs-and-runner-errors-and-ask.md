---
title: Record the agent model in run logs and runner errors, and ask a stalled agent why it stopped
status: backlog
created: 2026-11-24
---

## Description

Evidence, 2026-11-23: idle stalls ("was unchanged" / "still `doing` after 5 continuations") went from about none a day to several a day from 2026-11-20 (TASK-370, 391, 393, 467, 518, 519, 524, 557, 598, 629). Finding the cause took a manual dig through `~/.pi/agent/sessions/*/*.jsonl`: work sessions ran `gpt-6-luna` until 2026-11-20 12:03 and `gpt-6.1-terra` from 17:26 on, with no repository change between (so it came from how `chitty run` was started). Neither the run log (`.git/chitty/run/<ID>-<stamp>.log`) nor the error note says which agent command or model ran.

Proposals:
1. Write the resolved agent command (with model arguments from `work_model`/`review_model` or passed after `--`) as the first line of each run log, and include the model in the runner error note.
2. When a session ends with no handoff and no new non-ticket commit, send one more continuation that asks for a single line `Stopped because: <reason>` (with the first concrete step it would take next), and put that line in the error note. Today the agent's last words are vague ("I cannot substantiate a ticket defect or external blocker").
3. Stop sooner: two consecutive sessions with no non-ticket commit is already a clear stall; five continuations of 9-second sessions only add cost.
4. Let `chitty summary` (or `chitty list -s error`) group runner errors by cause and model, so a jump like this shows up without digging.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:21Z zesty-coral-newt → backlog
- 2026-11-24T22:21:21Z zesty-coral-newt: changed notes
