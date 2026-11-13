# Chitty design

Markdown-native task tracker for repos worked on by humans and coding agents.
A clean-room reimplementation of the idea behind Backlog.md, in Python, with
a file format that ordinary markdown tooling leaves alone and a much smaller
surface area.

Put in a chitty; an agent (or you) picks it up; the file is the record.

This plan is a guide, not a rulebook: past decisions and suggestions, some of
them old. Half of its original non-goals (reading tickets across branches,
file locks, format migration, shell completion, handling ID collisions) were
later built because use showed the need. When the evidence points elsewhere,
say so and change it.

One file per topic; read only the one you need.

- [Principles](principles.md)
- [Non-goals](non-goals.md)
- [Direction](direction.md)
- [Layout](layout.md)
- [IDs](ids.md)
- [Task file](task-file.md)
- [Config](config.md)
- [Dependencies](dependencies.md)
- [CLI](cli.md)
- [MCP](mcp.md)
- [Agent instructions](agent-instructions.md)
- [Pipeline and feedback](pipeline-and-feedback.md)
- [Stack](stack.md)
- [Next action and runner](next-action-and-runner.md)
- [Module layout](module-layout.md)
