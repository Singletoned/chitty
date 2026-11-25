---
title: chitty edit --plan - stores a literal dash
status: backlog
created: 2026-11-25
provisional: true
---

## Description

On TASK-639 I ran 'chitty edit TASK-639 --plan - <<EOF ... EOF'. The CLI accepted it and set the Plan section to a single '-' with no warning, so the approach was lost until I re-ran with --plan-file -. Evidence: 'chitty show TASK-639' showed '## Plan' followed by '-' after the first attempt. Suggestion: either read stdin for '-' as the other --\*-file options do, or reject a bare '-' with an error that names --plan-file.

## Notes

Suggestion origin: chitty-trial-round2-claude-haiku-task-639

## History

- 2026-11-25T22:28:33Z calm-ochre-quail → backlog
- 2026-11-25T22:28:34Z calm-ochre-quail: changed notes
