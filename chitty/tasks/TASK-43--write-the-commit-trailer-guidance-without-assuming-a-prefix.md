---
title: Write the commit-trailer guidance without assuming a prefix
status: todo
created: 2026-10-28
---

## Description

After chitty init --prefix CIRCUIT, the guide told agents to end commits with 'Task: TASK-N', so git log --grep found nothing. The first fix rendered the default prefix into the guide, but only init did so: `chitty guide`, the MCP instructions and guide tool, and the import's guide insertion still printed TASK-N, through a default parameter guide(prefix="TASK"). Rather than make every caller prefix-aware, write the guidance generically so that no rendering is needed: end commits with 'Task: <ID>' lines using the ticket's own ID (e.g. 'Task: TASK-12'), found with git log --grep <ID>. This covers HUMAN tickets and repos with old custom prefixes alike.

## Acceptance Criteria

- [ ] The guide says to end commits with 'Task: <ID>' lines using the ticket's own ID, with one concrete example, and that git log --grep <ID> finds them
- [ ] guide() takes no prefix and does no substitution; the prefix-rendering code from 91816cb is removed
- [ ] `chitty guide`, MCP instructions, the MCP guide tool, init and import all emit identical guide text
- [ ] init refreshes existing managed blocks, including ones that were rendered with a custom prefix
- [ ] Tests cover the generic text and the refresh of a previously rendered block; README and PLAN.md quotes updated

## Plan

Trace guide rendering and init refresh behavior, parameterize the managed guidance with the configured default prefix while retaining a rule for mixed contexts, add custom-prefix and refresh regressions, update quoted documentation, then run formatting and the complete check suite.

## Notes

Suggestion origin: circuitry

Decided with the human: default prefix plus 'use the ticket's own prefix' wording; no per-context listing.

Review failed: only `chitty init` renders the prefix. `guide(prefix: str = "TASK")` has a default, and the other callers rely on it: `chitty guide` (cli.py:553), the MCP server instructions and guide tool (mcp.py:25, mcp.py:51), and the import's guide insertion (import_backlog.py:256) all still print `Task: TASK-N`. Reproduced: `chitty guide` in a repo with prefix CIRCUIT prints TASK-N. Remove the default so every caller must pass the repository's prefix, and add a test for `chitty guide` in a custom-prefix repo. The MCP instructions are built at import time with no repo, so they need the prefix resolved when the server starts.

Redesigned with the human after the failed review: prefixes shouldn't name projects (see TASK-56), so the guide shouldn't depend on them. The custom-prefix rendering is reverted rather than extended.

## Summary

Rendered the managed guide with the default context prefix while telling agents to use each ticket’s own prefix in mixed contexts. Added custom-prefix and refresh coverage; updated README and PLAN.md. Verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → doing
- 2026-10-28 doing → todo
