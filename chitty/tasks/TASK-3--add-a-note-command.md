---
title: Add a note command
status: done
labels:
  - cli
created: 2026-10-25
---

## Description

Make notes a top-level command: `chitty note HUMAN-1 "blah blah"`. Today it is only `chitty edit ID --note TEXT`.

## Plan

Add a thin top-level note command that delegates to the same Edit note path as edit --note, preserve JSON output, and expose the equivalent MCP tool so both front ends remain aligned.

## Notes

Question: Should note duplicate edit behavior or introduce another mutation path? Answer: it will be a thin wrapper over Repo.edit(Edit(note=...)), preserving one implementation and output semantics.

Verified: CLI and MCP note commands share the existing edit path, return the updated task in JSON, and pass make check.
