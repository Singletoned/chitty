---
title: "Planning and review guides: weigh guide length when wording changes"
status: review
labels:
  - untestable
owner: plucky-indigo-eel
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

## Summary

- `src/chitty/roles/plan.md`, at the end of the `untestable` paragraph: "Agents read the guides and prompts in every session, so a ticket that adds text to agent guides or prompts says what it cuts to make room, or why they should grow."
- `src/chitty/roles/review.md`, at the end of the bullet starting "Fail only for an unmet criterion": "For an `untestable` ticket that changes guide or prompt text, if you can give a shorter wording that keeps every requirement, fail it with cause `work`, set `-s doing`, and put that wording in the note."
- `docs/plan/agent-instructions.md`: a new last bullet, after the one `TASK-640` added, records the decision.

Both new sentences say "agent guides or prompts" / "guide or prompt text" and name no file paths. This ticket adds text to the guides: it is what replaces the removed word-budget test, so the guides grow by about 60 words.

Verification: `make check`, run by `chitty edit -s review`.

## History

- 2026-11-23T12:34:55Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:43Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:41:20Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:24Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:24Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:44:56Z friendly-zinc-dormouse planning → todo
- 2026-11-23T14:37:02Z plucky-indigo-eel: changed owner
- 2026-11-23T14:37:02Z plucky-indigo-eel todo → doing
- 2026-11-23T14:50:47Z plucky-indigo-eel: changed summary
- 2026-11-23T14:50:47Z plucky-indigo-eel doing → review
