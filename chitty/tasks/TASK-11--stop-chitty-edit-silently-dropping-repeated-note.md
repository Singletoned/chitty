---
title: Stop chitty edit silently dropping repeated --note
status: done
labels:
  - cli
  - bug
created: 2026-10-25
---

## Description

`chitty edit ID --note A --note B` keeps only B: click takes the last value of a non-multiple option, so A is lost without any error. Either make --note repeatable (each one a paragraph, in order) or reject repeats; silent loss is the bug. Check other single-value options for the same problem.

## Plan

Make --note repeatable, preserve supplied order, and apply each value as a separate paragraph through the existing Task.with_note behavior. Check other single-value options for the same silent overwrite pattern.

## Notes

Question: Reject repeats or retain all notes? Answer: retain them in command-line order; it is useful batch behavior and avoids data loss.

Verified: repeated --note values are retained as separate Notes paragraphs in order. Other scalar edit options either intentionally overwrite or already reject conflicting file/value pairs. make check passes.
