# Agent instructions

- `chitty init` writes the managed block, `src/chitty/guide.md`, into
  `AGENTS.md` (creating it if needed) between marker lines:
  `<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->`
  and `<!-- chitty:end -->`.
- It replaces only the text between the markers. An old unmarked block is
  migrated once; malformed or ambiguous markers fail loudly for a person to fix.
- The block is a short pointer: Markdown and shell quoting rules, landing,
  review-note format, and which `chitty guide <role>` to run. The full rules
  are the role files, printed by
  `chitty guide work|review|repair|plan|cold-read|rebase`.
  `chitty guide setup` is the checklist for configuring `chitty run`.
  Role guides need `workflow = "runner"`: under `workflow = "tickets"`,
  `chitty guide <role>` refuses and the block leaves out the role list.
- `chitty guide` prints the block without markers; `chitty --help` points
  agents at it; MCP serves it as `chitty://guide`.
- The guides reach every repository that uses Chitty, so they name no
  language, library or repository.
- Do not test guide phrases or impose word budgets: phrase checks constrain
  rewording without testing behavior, and budgets can be raised trivially.
- Guide length is weighed where wording is decided instead (decided
  2026-11-23, `TASK-641`): a planning ticket that adds text to agent guides or
  prompts says what it cuts or why they should grow, and a reviewer fails an
  `untestable` guide change with cause `work` when it can offer a shorter
  wording that keeps every requirement.
