# Chitty

Markdown-native task tracker for repos worked on by humans and coding agents.
Put in a chitty; an agent (or you) picks it up; the file is the record.

Each task is one markdown file with YAML frontmatter under
`chitty/<context>/`, e.g. `chitty/tasks/TASK-12--add-search.md`. The files are
the only state: no database, no index. The tool only ever changes the lines
it means to, so prettier and mdformat leave its output alone and diffs stay
small. See `PLAN.md` for the full design.

## Install

Not yet on PyPI. From a checkout:

```sh
uv tool install .                 # CLI
uv tool install '.[mcp]'          # CLI plus `chitty mcp`
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
chitty add "Rotate prod password" -c human -d "Needs a person."
chitty move 1 human               # new ID there; references are rewritten
chitty archive HUMAN-1
chitty check                      # validate everything; non-zero on problems
chitty guide                      # instructions for coding agents
```

Every command takes `--json`. `chitty --help` and `chitty <command> --help`
are the reference.

Contexts are configured in `chitty.toml`. Contexts in other repos (for
posting tasks elsewhere) go in `~/.config/chitty/contexts.toml`:

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
