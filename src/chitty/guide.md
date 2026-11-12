## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks. When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.
Backticks run commands inside double-quoted shell arguments, so pass such text in single quotes. Avoid an apostrophe in the text, or write it as `'\''`.
Run `chitty --help` for the command reference.

A passing review lands through `chitty run`: it fast-forwards `main` only after
merging `main` into the ticket branch and running the configured setup and
checks. Agents started without `chitty run` should first merge `main` into the
branch in its worktree and run the configured checks; after they pass, only
fast-forward `main`. Do not merge or remove branches or worktrees as a reviewer.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

Every review note, whether passing or failing, has one line per criterion below
its `Reviewed:` or `Review failed (<cause>):` first line: `<number>: pass -
<evidence>` or `<number>: fail - <reason>`. Evidence is the command or test that
shows it. A test criterion passes only with evidence that the test fails without
the change.
