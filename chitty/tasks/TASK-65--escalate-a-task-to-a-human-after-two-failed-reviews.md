---
title: Escalate a task to a human after two failed reviews
status: backlog
created: 2026-11-01
---

## Description

When a task fails review twice, escalate it to a human instead of sending it back for another round: for example set it `blocked`, create a `-c human` task that links the failed reviews, and say so in the generated AGENTS.md guidance. Two agents can otherwise play ticket tennis indefinitely, each round "fixing" the reviewer's wording while nobody checks whether the human still wants the result. `chitty` could count `review → doing` transitions in History and refuse (or warn on) a third `-s review` without a human sign-off.

Example from circuitry, task CIRCUIT-78 (a map tile), 2026-10-29 to 2026-10-31. The user had looked at the map and said it was good. Then:

1. Review failed: browser tests needed an ignored `.env` in a fresh worktree (environmental; already fixed by another task).
2. Review failed on criterion 7's clause "halftone over the whole tile": the sea showed no halftone. The implementer moved the land image out of the SVG into a CSS background to change layering. That misaligned land and dots (towns drawn out at sea), and no review noticed because each only checked the halftone.
3. Review failed again on the halftone. The implementer reordered z-indexes.
4. Review failed again on the halftone, with pixel sampling as evidence.

The real cause, found only when the human stepped in, was that the SVG defining the halftone pattern was `display: none`, so the pattern could never render, whatever the layering. The human's verdict: "Fix it and close the ticket. I prefer a little bit of texture of any kind to the background, but it isn't worth playing ticket tennis over." Escalating after the second failure would have put the ambiguous criterion in front of the human two rounds and one regression earlier.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-01 → backlog
