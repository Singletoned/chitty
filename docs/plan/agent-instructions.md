# Agent instructions

- `chitty init` writes the managed block, `src/chitty/guide.md`, into
  `AGENTS.md` (creating it if needed) between marker lines:
  `<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->`
  and `<!-- chitty:end -->`.
- It replaces only the text between the markers. An old unmarked block is
  migrated once; malformed or ambiguous markers fail loudly for a person to fix.
- The block is a short pointer: Markdown and shell quoting rules, landing,
  review-note format, and which `chitty guide <role>` to run. The full rules
  are the role files, printed by `chitty guide work|review|repair|plan|cold-read`.
  `chitty guide setup` is the checklist for configuring `chitty run`.
- `chitty guide` prints the block without markers; `chitty --help` points
  agents at it; MCP serves it as `chitty://guide`.
- The guides reach every repository that uses Chitty, so they name no
  language, library or repository.
