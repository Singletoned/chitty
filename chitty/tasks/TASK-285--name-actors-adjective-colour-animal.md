---
title: Name actors adjective-colour-animal
status: todo
parent: TASK-283
created: 2026-11-11
---

## Description

- `_readable_name` in `src/chitty/actor.py` builds `adjective-animal` from two digest bytes: 625 names, so busy repositories get clashes (TASK-283).
- Add a `_COLOURS` tuple of 25 words (amber, bronze, coral, dusky, ebony, fawn, ginger, hazel, indigo, jade, khaki, lilac, maroon, navy, ochre, pearl, quartz, russet, silver, teal, umber, violet, white, yellow, zinc) and name actors `adjective-colour-animal`, such as `vivid-amber-yellowhammer`, with the adjective from `digest[0]`, colour from `digest[1]` and animal from `digest[2]`: 15,625 names.
- Names already in History stay as written.
- Update the shape assertion in `tests/test_actor.py` (`^[a-z]+-[a-z]+$`). `README.md` and `PLAN.md` hold no actor names.

## Acceptance Criteria

- [ ] A test shows the same session always getting the same name, matching `^[a-z]+-[a-z]+-[a-z]+$`, with its middle word from `_COLOURS`. It fails today.
- [ ] A test over many session IDs shows adjective and colour varying independently (more than 100 distinct pairs from 500 sessions).

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-285/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T16:09:08Z vivid-yellowhammer → backlog
- 2026-11-11T16:09:46Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T16:12:10Z vivid-yellowhammer: changed description
- 2026-11-11T16:12:11Z vivid-yellowhammer: changed description
- 2026-11-11T16:12:12Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T16:12:12Z vivid-yellowhammer cold-read → todo
