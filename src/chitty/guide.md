## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks.
Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
Run `chitty --help` for the command reference.

Never commit your changes on `main`. Outside ticket work, branch from it in a
worktree as `plan/<name>` or `hotfix/<name>`, run the checks, then fast-forward
`main`.
