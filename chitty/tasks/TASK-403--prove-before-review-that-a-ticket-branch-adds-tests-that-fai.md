---
title: Prove before review that a ticket branch adds tests that fail on main
status: todo
created: 2026-11-18
---

## Description

Reviewers must show each test criterion fails without the change, by hand. This is mechanical: before starting the reviewer, the runner could run the branch tests against the source on `main` (branch test files, `main` code) and record which new or changed tests fail, giving the reviewer that evidence, or failing the review when none do. At planning time no tests exist yet, so the planning-side version is the cold-read question "are the tests good", now in the cold-read guide. Needs planning: how to pick the changed tests generically for any language (the configured `check` runs everything), and what counts as a failure versus an import error.

## History

- 2026-11-18T20:24:14Z lively-quartz-crane → todo
