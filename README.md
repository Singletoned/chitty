# Chitty

Markdown-native task tracker for repos worked on by humans and coding agents.
Put in a chitty; an agent (or you) picks it up; the file is the record.

Each task is one markdown file with YAML frontmatter under
`chitty/<context>/`, e.g. `chitty/tasks/TASK-12--add-search.md`. The files are
the only state: no database, no index. The tool only ever changes the lines
it means to, so prettier and mdformat leave its output alone and diffs stay
small. See `PLAN.md` for the full design.

## Install

```sh
uv tool install chitty            # CLI
uv tool install 'chitty[mcp]'     # CLI plus `chitty mcp`
uvx chitty --help                 # run without installing
```

## Use

```sh
chitty init                       # create/upgrade config and register its machine-local project inbox
chitty import backlog-md          # convert a reviewed legacy backlog/ directory
chitty suggest other "Improve docs" -d "Explain setup."  # machine-local inbox
chitty pull                       # collect this repo's inbox as backlog tasks
# `add -c` names only a context in this repository; use `suggest` across projects.
chitty add "Add search" -d "Search titles and bodies." \
    --ac "Matches title" --ac "Case-insensitive" -l cli \
    --note "Useful context, repeatable."
chitty list
chitty show 1                     # bare numbers mean the default context
chitty edit 1 -s doing --plan "Use casefold()." --check 1
chitty edit 1 -s review
chitty edit 1 -s done --note "Reviewed: ready to merge."
chitty edit 1 --note "Safari needs a polyfill."
chitty edit 1 -s blocked --note "Awaiting a product decision."
chitty add "Refine sync idea" -s backlog  # stores a default refinement note
chitty add "Rotate prod password" -c human -d "Needs a person."
chitty move 1 human               # new ID there; references are rewritten
chitty archive HUMAN-1
chitty check                      # validate everything; non-zero on problems
chitty fix                        # repair safe problems; fail if any remain
chitty archive                     # process every completed task before a merge request
chitty guide                      # instructions for coding agents
```

Every command takes `--json`. `chitty --help` and `chitty <command> --help`
are the reference. Plain `chitty list` shows non-archived `todo`, `doing`,
`blocked`, and `review` tasks across every context; repeat `-c` or `-s` to filter,
including backlog and done tickets. Review is required before `done` by default;
set `review = false` in repository configuration to make it optional. Use `--parent TASK-1` to show a parent's direct children.
`--all` includes every status but never archive folders.
Empty lists explain their active filters on stderr while JSON stdout remains
`[]`. `chitty import backlog-md` refuses non-empty contexts, reports
mappings. It removes clean, tracked converted files in its import commit; use
`--keep-source` to retain all source files or `--remove-source` to force deletion
of dirty or untracked sources. Each task has a tool-managed trailing
`## History` that records its creation and status transitions. Finished tasks can include a `## Summary` handoff via
`chitty edit ID --summary TEXT`. To inspect or restore an archived task, work
with its file directly.

Enable tab completion by adding one of these lines to your shell startup file:

```sh
# bash
source <(_CHITTY_COMPLETE=bash_source chitty)
# zsh
eval "$(_CHITTY_COMPLETE=zsh_source chitty)"
```

Set `autoformat = "mdformat"` in repository config to run a formatter on each
written task file before any autocommit. Commits for task work should end with
`Task: TASK-N` lines so `git log --grep TASK-N` finds a ticket's code; use the
ticket's own prefix when contexts differ. This is a convention, not an enforced
check. Set `archive = "delete"` to delete
completed task files at merge-request time instead of moving them to `archive/`;
it also removes exact `depends_on` entries and requires complete Git history to
avoid reusing IDs. The default, `archive = "move"`, retains task files.

Contexts are configured in `chitty.toml` or `[tool.chitty]` in `pyproject.toml`
(not both). To send work to another repository, use `chitty suggest PROJECT`;
the receiving repository imports it with `chitty pull`. `PROJECT` is a
registered name unless it contains `/`, is `.`, or starts with `~` or `.`; those
path-shaped values resolve a local Chitty repository.

## Migrating from Backlog.md

From a clone of the legacy repository, run `chitty init`, then
`chitty import backlog-md`. Review its report: statuses declared in
`backlog/config.yml` become backlog with one summary per status, unknown statuses
become backlog notes, unsupported headings are demoted into the description, and
non-task files or folders are listed rather than imported. Run `chitty check`,
review and commit the generated tasks. Clean converted source files, including
`backlog/config.yml`, are removed by the import; delete any remaining reported
non-task files or folders when accepted.

## Develop

```sh
make install    # uv sync --all-extras; npm ci (pinned prettier)
make check      # ruff, pyright, unittest
make format
```
