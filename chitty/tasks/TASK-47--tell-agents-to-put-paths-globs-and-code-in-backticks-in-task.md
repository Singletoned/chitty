---
title: Tell agents to put paths, globs and code in backticks in task text
status: backlog
created: 2026-10-28
---

## Description

An agent wrote the criterion 'static/photos/*.jpg are copied into output/' with 'chitty add --ac'. The bare '*' is a CommonMark emphasis delimiter. It only renders literally because the line has no second '*'; the project formatter escaped it as '\*'. A formatter can't tell that a glob is code, so the fix belongs where agents write the text. Proposal: (1) add one line to the guide 'chitty guide' prints (the AGENTS.md block), e.g. 'Put paths, globs, commands, IDs and code in backticks in titles, descriptions and criteria.'; (2) optionally, have 'chitty check' warn, not error, on path-like tokens outside code spans (containing '/' together with '*', '.' or '_'). Don't auto-wrap tokens: guessing would sometimes change the meaning.

## Notes

Suggestion origin: circuitry

Needs refinement before implementation: decide whether this ticket is limited to mandatory guide wording or also includes the optional `chitty check` warning, and add acceptance criteria for the chosen scope. A warning heuristic needs examples and false-positive expectations.

## History

- 2026-10-28 → backlog
