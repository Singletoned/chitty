# MCP

- `chitty mcp` runs a stdio server (`MCPServer`, mcp ≥ 2).
- Tools mirror the CLI, with the same names and arguments: `add`, `suggest`,
  `inbox`, `whoami`, `list`, `show`, `edit`, `note`, `move`, `renumber`,
  `archive`, `check`, `fix`, `path`, and read-only `next`. They return the
  CLI's `--json` output; a Chitty error is a tool error.
- One resource, `chitty://guide`: the managed `AGENTS.md` block.
- An optional extra, `chitty[mcp]`, because `mcp` pulls in starlette, uvicorn
  and httpx. Agents with a shell use the CLI with `--json`. Without the extra,
  `chitty mcp` exits with an error saying so.
