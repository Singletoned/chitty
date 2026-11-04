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

Found by the third `TASK-126` review on 2026-11-04. `_readable_name` in `src/chitty/actor.py` hashes a session ID to an adjective and an animal: 16 of each, so 256 names. Two sessions share a name about 1 time in 256, more often the more sessions a repository has seen. So a reviewer can be refused as if they had done the work, and History can attribute one session's changes to another. The refusal is loud and `--override-review-independence` gets past it, so this is low priority, but the risk grows as more work runs unattended.

Add two hex characters from `digest[2]` to the name, as in `eager-jaguar-3f`, giving 65,536 names while staying readable. `digest[0]` and `digest[1]` already pick the words. The pattern in `tests/test_actor.py` line 30 asserts the old shape and must change. Nothing else depends on it: History parsing and `review_work` treat the name as an opaque string. Names already in History stay as written, because they are only labels; `review_work` compares a session's name now with names recorded earlier, so a session running across the change would stop matching its old name, which only matters for one running at that moment.

Out of scope: a registry of names in use, and changing `CHITTY_ACTOR`, which a person sets directly.

## Acceptance Criteria

- [ ] `README.md` and `PLAN.md` describe the name form where they mention it
- [ ] Tests show the same session always getting the same name in the new form, two IDs that share an adjective and animal getting different names, and a History line with a new-form name read back by `review_work`

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: my numbers, which were wrong: 16 of each, confirmed by importing the module, so 256 names and 65,536 after the change; which digest byte to use; and the existing test asserting the old shape. Confirmed: no parsing depends on the name's shape. Confirmed too: a session running across the change stops matching its old name, so it would not be refused as reviewing its own work; rejected as a problem, because it lasts for one session at one moment, and a new session is started per ticket. Rejected: a test for reading old-form lines, because `review_work` compares strings and old lines are untouched. A test for `CHITTY_ACTOR`, which the override test covers and this does not change. How the test finds two colliding IDs, which is the worker's choice.

## History

- 2026-11-04T12:40:34Z lively-panda → todo
- 2026-11-04T12:41:27Z lively-panda: changed description, acceptance criteria, notes
