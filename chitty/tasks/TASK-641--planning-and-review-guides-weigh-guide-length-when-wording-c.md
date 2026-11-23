---
title: "Planning and review guides: weigh guide length when wording changes"
status: todo
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-640
created: 2026-11-23
---

## Description

`tests/test_guide_word_budget.py` used to cap guide word counts. `TASK-640` removes it, because the numbers were arbitrary and the worker met them partway through a ticket. The concern behind them is real: agents read the guides in every session in every repository that uses Chitty, and the guides grew to about 4,100 words before the budget (TASK-352). Decision (the person, 2026-11-23): weigh length where the wording is decided, not in a test.

Change:
- `src/chitty/roles/plan.md`, near the paragraph about `untestable` tickets: a ticket that adds text to agent guides or prompts says what it cuts to make room, or why the guides should grow.
- `src/chitty/roles/review.md`, as one sentence in the bullet starting "Fail only for an unmet criterion": for an `untestable` ticket that changes guide or prompt text, fail it with cause `work` and set `-s doing` when you can give a shorter wording that keeps every requirement; put that wording in the note.

One or two sentences each. Keep the wording general: the guides reach every repository, which may call them something else, so say "agent guides or prompts", not file paths from this repository. Record the decision in `docs/plan/agent-instructions.md`, at the end of its list, after the bullet `TASK-640` adds. The Change list is the whole definition of done; the reviewer judges the sentences against it.

## History

- 2026-11-23T12:34:55Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:43Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:41:20Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:24Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:24Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:44:56Z friendly-zinc-dormouse planning → todo
