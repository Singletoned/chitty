## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks. When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.
Backticks run commands inside double-quoted shell arguments, so pass such text in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
Run `chitty --help` for the command reference.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.
