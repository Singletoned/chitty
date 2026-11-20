## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks. When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.
Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
Run `chitty --help` for the command reference.
