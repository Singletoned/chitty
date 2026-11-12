# MCP

`chitty mcp` runs a stdio server. Tools mirror the CLI one-to-one with the
same names and argument names: `add`, `suggest`, `inbox`, `whoami`, `list`, `show`,
`edit`, `note`, `move`, `renumber`, `archive`, `check`, `fix`, `path`, and the
read-only `next`. They return the same JSON
the CLI prints with `--json`. One resource, `chitty://guide`, returning the
same text as the AGENTS.md block. Tool descriptions state the rules (one
task per session, write Plan before coding, tick criteria as you go).

The `mcp` package pulls in starlette, uvicorn, httpx and friends, so it is an
optional extra: `uv tool install 'chitty[mcp]'`. Agents with a shell can use
the CLI with `--json` and need none of it. `chitty mcp` without the extra
exits with an error saying so.
