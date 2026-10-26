---
title: Publish chitty to PyPI
status: done
created: 2026-10-23
---

## Description

The plan assumes `uv tool install chitty` and `uvx chitty`. Check the name is available and publish.

## Acceptance Criteria

- [x] Pending publisher registered at pypi.org/manage/account/publishing/ (owner Singletoned, repo chitty, workflow release.yml, environment pypi)
- [x] GitHub environment pypi created (Settings → Environments)
- [x] main pushed: git push -u origin main
- [x] Tag pushed: git tag v0.1.0 && git push origin v0.1.0, and the release workflow succeeded
- [x] README install line updated now chitty is on PyPI

## Notes

Licence (MIT), author, keywords and classifiers added to pyproject.toml. uv build verified: the wheel holds only the chitty package and LICENSE. Project URLs wait for a public repo.

Project URLs and .github/workflows/release.yml added; publishing is by trusted publishing on tag push.

HUMAN INPUT NEEDED: publishing requires the repository owner to configure PyPI trusted publishing and create the GitHub pypi environment, then explicitly authorize production GitHub/PyPI access and the main/tag pushes. I have not accessed either production system.

https://pypi.org/project/chitty/0.1.1/

Verified on pypi.org: 0.1.0 and 0.1.1 published; release workflow runs for v0.1.0 and v0.1.1 succeeded. README install now uses PyPI.
