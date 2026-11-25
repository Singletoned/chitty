---
title: Move the global Pi back to a current release once the GPT-6 reasoning fix ships
status: todo
labels:
  - bug
priority: high
created: 2026-11-25
---

## Description

On 2026-11-25 the global Pi was downgraded from 1.6.0 to 1.5.2 (`npm install -g @earendil-works/pi-coding-agent@1.5.2`), decided with the person. Do not run `pi update` or reinstall a newer Pi until this ticket is done.

Why: Pi 1.6.0 sends `reasoning.effort: "medium"` and puts the chosen level in `configuration_update` items for GPT-6 models (`compat.supportsMidConvoEffort`). For `gpt-6-luna` on the Codex backend this leaves the model with almost no reasoning: in this repository's Pi sessions, luna had thinking on 56-70% of calls from 2026-11-08 to 2026-11-20 and 0-15% from 2026-11-23, when it was first used on 1.6.0 (installed 2026-11-21). Its broken tool calls (empty bash commands, edits that replace a line with itself) rose from 1-2% to 10-25%, and workers returned most tickets to `planning` with notes saying the ticket had no defect. In a trial on 2026-11-25 (`tmp/worker-trial/`), the same ticket on Pi 1.5.2 had thinking on 42 of 53 calls; on 1.6.0, 0 of 21. Upstream: https://github.com/earendil-works/pi/issues/12361 (closed; the fix was not in a release as of 2026-11-25, when 1.6.0 was the latest on npm).

Done when: a Pi release after 1.6.0 includes the fix; install it globally, run one `chitty run --ticket` work session with `work_model = "openai-codex/gpt-6-luna"`, and confirm from its session file in `~/.pi/agent/sessions` that most assistant messages have a `thinking` block. If not, stay on 1.5.2.

## History

- 2026-11-25T12:06:58Z sunny-hazel-gannet → todo
