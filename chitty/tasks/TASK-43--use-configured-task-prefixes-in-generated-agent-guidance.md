---
title: Use configured task prefixes in generated agent guidance
status: backlog
created: 2026-10-28
---

## Description

After running chitty init --prefix CIRCUIT, the generated AGENTS.md says commits should end with 'Task: TASK-N'. The project's actual IDs are CIRCUIT-N, so following the generated instruction would make git-log task lookup fail. Render the configured context prefix in this guidance, or state the generic placeholder explicitly.

## Notes

Suggestion origin: circuitry

## History

- 2026-10-28 → backlog
