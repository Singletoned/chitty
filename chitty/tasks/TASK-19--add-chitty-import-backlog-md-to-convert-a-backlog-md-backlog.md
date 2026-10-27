---
title: Add chitty import backlog-md to convert a Backlog.md backlog
status: doing
labels:
  - cli
  - import
priority: high
depends_on:
  - TASK-17
  - TASK-18
created: 2026-10-26
---

## Description

Several of our repos (circuitry, sump) use Backlog.md and should move to chitty. Add an explicit converter, chitty import backlog-md, which reads a repo's backlog/ directory and writes the equivalent chitty tasks, so each repo's migration is one command rather than a one-off script.

Mapping:
- Statuses: To Do → todo, In Progress → doing, Done → done. Any other configured status (circuitry's Backburner) → backlog, with a note recording the original status. Drafts → backlog.
- IDs: TASK-n keeps its number. Subtasks (TASK-n.m) get the next free numbers and a parent field pointing at TASK-n. Every reference, in depends_on and in body text, is rewritten to the new ID, and each converted task gets a note recording its Backlog.md ID.
- Frontmatter: title, labels and priority carry over; dependencies → depends_on; created_date → created (date only); the first assignee → owner. ordinal and updated_date are dropped (git keeps the dates). references and modified_files move into the body as lists.
- Sections: Implementation Plan → Plan, Implementation Notes → Notes, Final Summary → Summary, Comments → Notes. Backlog.md's SECTION/AC marker comments are removed. Any other ## heading (circuitry has about 10 one-offs) is demoted to ### under the section it follows, so nothing is lost.
- Completed and archived tasks follow the repo's archive setting.
- decisions/, docs/ and milestones/ are not tasks: list them, and leave them in place for a person to decide on.

The import refuses to run if the chitty context already has tasks, so it can't merge two histories by accident. It replaces the Backlog.md guidelines block in AGENTS.md with the chitty block, and leaves deleting backlog/ to the user.

## Acceptance Criteria

- [ ] chitty import backlog-md converts every task in backlog/tasks, drafts, completed and archive using the mapping above
- [ ] Subtasks get flat IDs with parent set, and every reference to an old ID in frontmatter or body is rewritten
- [ ] Converted files pass chitty check and contain no Backlog.md marker comments
- [ ] Unknown statuses, demoted headings and non-task files are reported in the command's output
- [ ] It refuses to run when the target context already has tasks
- [ ] The AGENTS.md Backlog.md block is replaced with the chitty block
- [ ] Tested against a copy of circuitry's backlog/ (66 tasks, 25 subtasks, a custom Backburner status) and sump's
- [ ] README and PLAN.md describe the command; PLAN.md's 'no migrations' scope note is updated

## Plan

Inspect representative Backlog.md task files from circuitry and sump, build a strict parser and dry conversion plan, then add the import command with fixtures covering ID/reference rewrites, sections, archive policy, reporting, and refusal safeguards.

## Notes

This ticket is too large for one independently verifiable change: it combines a legacy Markdown parser, ID/reference migration, atomic repository writer, archive/autocommit integration, AGENTS migration, reporting, docs, and two real-backlog acceptance suites. I recommend splitting it into parser/mapping, importer command+safety, and fixture-based circuitry/sump compatibility tasks before implementation.

Owner directed work to continue on other available tickets while this oversized migration remains pending decomposition approval.
