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
chitty init                       # chitty.toml, chitty/tasks/, AGENTS.md block
chitty add "Add search" -d "Search titles and bodies." \
    --ac "Matches title" --ac "Case-insensitive" -l cli
chitty list
chitty show 1                     # bare numbers mean the default context
chitty edit 1 -s doing --plan "Use casefold()." --check 1
chitty edit 1 --note "Safari needs a polyfill."
chitty add "Refine sync idea" -s backlog  # stores a default refinement note
chitty add "Rotate prod password" -c human -d "Needs a person."
chitty move 1 human               # new ID there; references are rewritten
chitty archive HUMAN-1
chitty check                      # validate everything; non-zero on problems
chitty fix                        # repair safe problems; fail if any remain
chitty archive                     # archive every completed task before a merge request
chitty guide                      # instructions for coding agents
```

Every command takes `--json`. `chitty --help` and `chitty <command> --help`
are the reference. Plain `chitty list` shows non-archived `todo` and `doing`
tasks across every context; repeat `-c` or `-s` to filter, including backlog
and done tickets. `--all` includes every status and archived task. Empty lists
explain their active filters on stderr while JSON stdout remains `[]`.

Set `autoformat = "mdformat"` in repository config to run a formatter on each
written task file before any autocommit.

Contexts are configured in `chitty.toml` or `[tool.chitty]` in `pyproject.toml`
(not both). Contexts in other repos (for posting tasks elsewhere) go in
`~/.config/chitty/contexts.toml`:

```toml
[contexts.notes]
repo = "~/notes"
```

## Develop

```sh
make install    # uv sync --all-extras; npm ci (pinned prettier)
make check      # ruff, pyright, unittest
make format
```
