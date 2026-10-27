---
title: Parse and map a single Backlog.md task file
status: done
labels:
  - import
parent: TASK-19
created: 2026-10-27
---

## Description

Pure conversion of one Backlog.md task file into a chitty task, using the mapping in TASK-19. No IDs are renumbered and no files are written; this is the building block for the importer.

## Acceptance Criteria

- [x] Statuses map To Do→todo, In Progress→doing, Done→done; drafts and any other status → backlog with a note recording the original
- [x] Frontmatter maps title, labels, priority, dependencies→depends_on, created_date→created (date only), first assignee→owner; ordinal and updated_date dropped; references and modified_files become body lists
- [x] Sections map Implementation Plan→Plan, Implementation Notes→Notes, Final Summary→Summary, Comments→Notes; SECTION/AC marker comments removed; other ## headings demoted to ### under the preceding section
- [x] Returns what it could not map exactly (unknown statuses, demoted headings) for the importer to report
- [x] Unit tests use small committed sample files; converted output passes the chitty parser

## Plan

Create a pure importer parser/mapping module from representative committed fixture files, preserve task content through the existing model renderer, and report lossy mappings. Add focused unit tests before marking complete.

## Notes

Implemented an initial pure converter and manually parsed/rendered representative Sump and Circuitry task files. Next: add committed fixtures and unit coverage for mapping edge cases.

Added focused conversion regression coverage for custom status, mapped fields, checked criteria, Summary, demoted headings, report output, and parser round-trip. References/modified_files now become Description lists. Draft-location mapping and committed fixture files remain.

Criteria 1–4 verified via focused test: status and field mapping, sections/marker removal/demotion, reports, and parser round-trip. Criterion 5 remains open pending conversion of inline sample to a committed fixture file.

Replaced the inline conversion sample with committed tests/fixtures/backlog/task-7.3.md; full make check passes.
