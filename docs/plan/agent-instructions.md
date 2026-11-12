# Agent instructions

`chitty init` appends this short block to `AGENTS.md` (creating it if absent),
idempotently, using strict markers around the managed text:

```markdown
<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->

...

<!-- chitty:end -->
```

It replaces only the text between the marker lines. An old unmarked block is
migrated once; malformed or ambiguous markers fail loudly so a person can
remove them:

```markdown
## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks.
Run `chitty --help` for the command reference.

When starting an agent by hand, run the matching focused guide:
- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.
```

That is the whole pointer prompt. The complete work, review, and planning rules
live in the packaged role files printed by `chitty guide <role>`. `chitty guide
setup` is a separate checklist for configuring `chitty run` from the main
checkout, and `chitty guide --help` lists the roles with usage examples.
Statuses are fixed, so the block is always correct. `chitty guide` prints the
same unmarked block, and `chitty --help` points agents at it.
