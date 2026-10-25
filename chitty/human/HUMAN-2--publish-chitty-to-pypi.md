---
title: Publish chitty to PyPI
status: todo
created: 2026-10-23
---

## Description

The plan assumes `uv tool install chitty` and `uvx chitty`. Check the name is available and publish.

## Acceptance Criteria

- [ ] Pending publisher registered at pypi.org/manage/account/publishing/ (owner Singletoned, repo chitty, workflow release.yml, environment pypi)
- [ ] GitHub environment pypi created (Settings → Environments)
- [ ] main pushed: git push -u origin main
- [ ] Tag pushed: git tag v0.1.0 && git push origin v0.1.0, and the release workflow succeeded
- [ ] README install line updated now chitty is on PyPI

## Notes

Licence (MIT), author, keywords and classifiers added to pyproject.toml. uv build verified: the wheel holds only the chitty package and LICENSE. Project URLs wait for a public repo.

Project URLs and .github/workflows/release.yml added; publishing is by trusted publishing on tag push.
