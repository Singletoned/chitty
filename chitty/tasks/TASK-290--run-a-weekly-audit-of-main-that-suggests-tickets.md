---
title: Run a weekly audit of `main` that suggests tickets
status: backlog
created: 2026-11-11
---

## Description

- An occasional pass on `main`, queued by the human as a `low` ticket (TASK-296), runs security and test-quality tools and turns each new finding into a suggestion in this repository's inbox, for the planner to triage.
- One entry point, `make audit`, running `scripts/audit.py`. Each tool is a small adapter returning findings with a stable key (tool, rule, file). A finding whose key already appears in a ticket title, open or archived, is skipped, so a weekly run repeats nothing.
- Children add the runner and one tool each: bandit, pip-audit, `npm audit`, trivy (filesystem: vulnerabilities, secrets, misconfiguration), and mutation testing. Add checkov when the repository gains containers or infrastructure code.
- Python tools are dev dependencies; trivy is a system install, and the audit fails plainly if it is missing.

## History

- 2026-11-11T16:18:07Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:46Z vivid-yellowhammer: changed description
