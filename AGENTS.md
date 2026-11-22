# Agents

Chitty is a markdown-native task tracker. The design is in `docs/plan/`, one
file per topic, indexed in `docs/plan/README.md`. Before changing behaviour,
read only the file you need. It holds suggestions and past decisions, not
rules, and parts are old: update it when a decision changes.

- `make install` once (Python deps including the `mcp` extra, and the pinned
  prettier used by the round-trip tests).
- In this repository run `main`'s Chitty, `.venv/bin/chitty` in the main
  checkout, not the global PyPI `chitty`: `main` is usually ahead of PyPI.
- `make check` (ruff, pyright and unittest; formatter tests use pinned prettier)
  before every commit. `sh scripts/check_linux.sh` checks committed `HEAD` in a
  Linux container. `make format` to fix formatting.
- Tests use `unittest` and write real files in temp dirs; no filesystem
  mocking. Tests that use the inbox must inherit `RepoTestCase`, which assigns
  a temporary `XDG_DATA_HOME` so they never touch the real inbox. The formatter
  tests fail, never skip, if prettier or mdformat is missing.
- `make check` uses fixed examples (profile `check`) so it repeats; `make test`
  draws new random examples (profile `thorough`) to find new edge cases. A
  property test that fails is a real failure: fix it, do not rerun.
- Put a ticket's new guide tests in their own file, `tests/test_guide_<topic>.py`,
  not at the end of `TestGuide` in `tests/test_cli.py`, where every guide
  ticket's tests collide.
- The guides (`src/chitty/guide.md` and `src/chitty/roles/`) reach every
  repository that uses Chitty, in any language. Keep their advice general:
  nothing specific to this repository, Python or Hypothesis.
- `cli.py` and `mcp.py` stay thin: behaviour lives in `store.py` and
  `model.py` so the two front ends cannot diverge.
- Other agents commit in this checkout at the same time. Stage only the paths
  you changed; never `git add -A` or all of `chitty/`.
- Writing tickets with the human? Cold-read them, as
  `docs/plan/pipeline-and-feedback.md` describes. If you were given a ticket to
  work on or review, skip this: it is not your step.
- Releases: `make release` refuses while any ticket labelled `blocks-release`
  is not `done`. It works in a temporary worktree at `main` (`scripts/release.sh`),
  so the main checkout may be dirty and runners may keep landing: it bumps and
  checks the version there, runs the Linux check, pushes the release commit and
  tag, then merges the
  tag into the local `main`.
  `.github/workflows/release.yml` checks, builds and publishes to PyPI by
  trusted publishing (environment `pypi`). `make release` then waits for that
  run (`scripts/watch_release.py`): on success it installs the released version
  as the global `chitty`; on failure it records the failure with `sump capture
  chitty` and exits non-zero.
- Branches never change `__version__` in `src/chitty/__init__.py`; `make release`
  chooses the published bump. Never edit `chitty.toml` or the managed block below,
  or run `chitty init`, on a ticket branch. The main checkout's `chitty` upgrades
  setup files after the work lands (TASK-212).
- Whoever writes, works or reviews a ticket may add `needs-minor` when users must
  notice or act on the change: a new required setting, changed default or
  selection rule, something needing `chitty init` re-run, or a removed command or
  option. Only `done` tickets labelled `needs-minor` count toward a minor release.

<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->

## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks.
Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
Run `chitty --help` for the command reference.

A ticket lands on `main` only after its review passes; a worker never lands
its own ticket. Under `chitty run`, the runner lands a passing review: it
fast-forwards `main` only after rebasing the ticket branch onto `main` and
running the configured setup and checks, so do not merge or remove branches or
worktrees as a reviewer. A reviewer started without `chitty run` whose review
passed should first rebase the branch onto `main` in its worktree and run the
configured checks; after they pass, only fast-forward `main`.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

Workers may resolve a small omission when the ticket and existing code or tests
point to one clear, cheap-to-reverse default. It must preserve requirements
and acceptance criteria and introduce no new user-visible policy, command, or
setting. Record `Decided: <case> -> <choice>, because <reason>`, cite the
precedent, and add a focused test where testable. Reviewers check the choice,
precedent, and test against the same boundary. Do not invent or weaken a test
needed to verify a stated criterion.

Apart from that exception, workers and reviewers return a ticket to `planning`
for missing or contradictory requirements, an unresolved design decision, a
wrong claim about the code, files or other tickets, a criterion that cannot be
verified as written or would pass with nothing built, a test a criterion needs
that the ticket does not describe (its fixture, action and assertions), or a
ticket too large to finish in one session. Stop implementation, not
investigation, at the first planning blocker. Before changing status, finish
reading the ticket and checking relevant code and tests for the remaining
requirements. Report all actionable planning issues in one note with evidence
and the decision or correction needed. Say what could not be checked and why,
and continue with independent checks without speculating or expanding scope.
Preserve existing implementation work and follow normal
planning and cold-read readiness before resuming. Implementation defects against
clear requirements return to `doing`; external obstacles requiring help go to
`blocked`.

Every review note, whether passing or failing, has one line per criterion below
its `Reviewed:` or `Review failed (<cause>):` first line: `<number>: pass -
<evidence>` or `<number>: fail - <reason>`. Evidence is the command or test that
shows it. A test criterion passes only with evidence that the test fails without
the change.

<!-- chitty:end -->

## Learned Rules (managed by /learn)
<!-- pi:learn:start -->
- Never make implementation or documentation fixes directly on `main`, including fixes made by the assistant. Create or use a dedicated workspace/worktree, commit the change there, and merge it into `main` only after verification. Preserve isolation because multiple sessions may run concurrently.
<!-- pi:learn:end -->
