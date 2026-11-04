---
title: Stop different sessions sharing an actor name
status: todo
labels:
  - bug
priority: low
parent: TASK-106
created: 2026-11-04
---

## Description

Found by the third `TASK-126` review on 2026-11-04. `_readable_name` in `src/chitty/actor.py` hashes a session ID to an adjective and an animal: 17 of each, so 289 names. Two sessions share a name about 1 time in 289, more often the more sessions a repository has seen. So a reviewer can be refused as if they had done the work, and History can attribute one session's changes to another. The refusal is loud and `--override-review-independence` gets past it, so this is low priority, but the risk grows as more work runs unattended.

Add two hex characters of the digest to the name, as in `eager-jaguar-3f`, giving about 74,000 names while staying readable. Names already in History stay as written, because they are only labels; `review_work` compares a session's name now with names recorded earlier, so a session running across the change would stop matching its old name, which only matters for one running at that moment.

Out of scope: a registry of names in use, and changing `CHITTY_ACTOR`, which a person sets directly.

## Acceptance Criteria

- [ ] A test shows the same session always getting the same name, in the new form, and two IDs that share an adjective and animal getting different names
- [ ] `README.md` and `PLAN.md` describe the name form where they mention it

## History

- 2026-11-04T12:40:34Z lively-panda → todo
