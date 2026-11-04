---
title: Mark Chitty's block in `AGENTS.md` with strict begin and end comments
status: todo
priority: medium
parent: TASK-140
created: 2026-11-04
---

## Description

`chitty init` finds its block in `AGENTS.md` with a pattern: from `## Chitty` to the next `## ` heading or the end of the file. It cannot know where its own text stops, so unheaded text a person adds after the block is deleted, the blank line before a following section is lost, and a second `## ` line in the guide would leave part of the old block behind. Decided by the human on 2026-11-04: `chitty init` should know exactly what it replaces.

Wrap the block in `AGENTS.md` in strict comments, which also say it was inserted by Chitty:

```markdown
<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->
## Chitty
...
<!-- chitty:end -->
```

In `init_repo` in `src/chitty/store.py`, replace exactly the text from the begin line to the end line, and nothing around it, using plain string slicing rather than `re.subn`, which treats the guide as a template. A marker counts only as a whole line equal to the expected text. `src/chitty/guide.md` itself has no markers: `chitty guide` and `chitty://guide` print the same text as now, and `init_repo` adds them.

- Exactly one begin line followed by one end line: replace between them.
- No markers and no `## Chitty` line: append the block, as now.
- Anything else with markers (one without the other, reversed, or more than one pair): fail with a message naming `AGENTS.md`, and write nothing. A person must repair it, because Chitty no longer knows what is its own.
- No markers but a `## Chitty` line, which is every existing repository: migrate once by using the old pattern to find the block, then writing it with markers. Comparing against known versions instead would mean shipping a record of all 26 versions of `guide.md` in Git, and the human preferred markers. The change goes through Git, so it can be seen and undone. Keep the blank line before a following section, and report the migration on stderr.

Bump `__version__`, so existing repositories upgrade. This repository's `AGENTS.md` then upgrades through `chitty init` in the main checkout after landing, so do not edit its block by hand on the branch.

Out of scope: the guide's content, which is `TASK-143`, and `chitty.toml`.

## Acceptance Criteria

- [ ] Tests show a marked block replaced with text before and after it unchanged byte for byte, including unheaded text after it and a guide containing a backslash, and a second `chitty init` changing nothing
- [ ] Tests show a new `AGENTS.md`, and one with content but no block, getting the block with both markers, and `chitty guide` printing no markers
- [ ] Tests show a begin with no end, an end with no begin, reversed markers and two pairs each failing with a message naming `AGENTS.md`, with the file unchanged
- [ ] Tests show an old block migrated to markers with a following section keeping its heading and blank line, and a message on stderr
- [ ] `README.md` and `PLAN.md` describe the markers, and `__version__` is bumped above `main`'s

## History

- 2026-11-04T12:31:58Z lively-panda → todo
