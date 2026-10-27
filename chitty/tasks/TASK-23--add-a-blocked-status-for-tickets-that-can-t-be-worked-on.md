---
title: Add a blocked status for tickets that can't be worked on
status: todo
labels:
  - cli
created: 2026-10-27
---

## Description

A blocked ticket is one someone has judged cannot proceed without help: a decision, a split, or something outside the repo. It differs from backlog (not yet refined) and from depends_on (waiting on another ticket, which chitty can see). TASK-14 and TASK-19 both sat at doing while waiting on the human, with only a note to say so; status is the field everyone reads.

## Acceptance Criteria

- [ ] blocked is a status, ordered between doing and done (backlog → todo → doing → blocked → done) in every context
- [ ] Setting -s blocked requires a --note in the same command (CLI and MCP); without one it is an error naming the fix
- [ ] Plain chitty list shows blocked tasks alongside todo and doing; -s blocked filters to them
- [ ] Unblocking is setting -s todo or -s doing; checklist and Plan are left as they are
- [ ] blocked is never set automatically from open depends_on
- [ ] Shell completion includes blocked
- [ ] Agent guide: when you can't proceed, set -s blocked with the reason and move on; never pick up a blocked ticket; also file a -c human ticket and depends_on it when a person must act outside the repo
- [ ] Tests, PLAN.md, README and AGENTS.md updated
