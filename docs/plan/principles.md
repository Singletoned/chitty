# Principles

- **Files are the truth.** No database, index or cache. A directory scan is
  fast enough for thousands of tickets.
- **One ticket, one file, one writer.** No locking or automatic conflict
  repair.
  - Reads use committed state from every local and remote-tracking branch,
    taking each ticket's most recently changed version. Uncommitted files in
    the current worktree override it.
  - A write refuses when the latest version is on another branch, and names
    that branch's worktree. Writes never cross branches.
  - So worktrees need `autocommit = true` (or commit every Chitty write).
  - IDs are sequential and tickets are created centrally, so branches rarely
    collide; `check` reports it when they do.
- **Simple first.** Add complexity when use shows the need.
- **Plain Markdown.** Every ticket file survives the supported formatters
  unchanged in meaning ([Task file](task-file.md)). No HTML comments, sentinel
  markers or numbers in checklist text.
- **Loud errors.** A malformed file is rejected with a path and a reason, never
  silently repaired. `chitty check` is the compile step.
- **Chitty does the bookkeeping.** Whatever the tool can work out or keep
  consistent (derived status, references to finished tickets, dates, who did
  what), it does. Whatever a script can do reliably (branches, worktrees,
  setup, claiming, merging), `chitty run` does. Agents get only the judgement.
- **Chitty never calls a model.** Models sit only in the worker and reviewer
  seats. Which agent is configuration: agent-specific code stays in
  integrations.
- **The tool carries the rules.** Validation and `--help` document them; agent
  instructions stay short and static.
- **Minimal diffs.** Never touch a line that did not change; never write an
  unchanged file.
- **Projects and suggestions.** Each repository has a validated lower-case
  `project` name. `init` registers its machine-local inbox (XDG data) and
  refuses a name another repository owns. `suggest` writes an idea to another
  project's inbox; `inbox` lists them; `inbox --pull` imports them as backlog
  tickets.

## Setup and upgrades

- `chitty init` is idempotent: it adds missing setup, refreshes the managed
  `AGENTS.md` block, and migrates formats.
- It installs the machine-wide Pi extension only from a main checkout (or a
  directory outside Git); linked worktrees skip machine-wide setup.
- Reads work with older setup; writes need it current. With
  `autocommit = true`, Chitty upgrades and commits setup separately before the
  write; otherwise it fails and says to run `chitty init`.
- Upgrades happen only in the main checkout. In a linked worktree a write
  skips the upgrade and the stale-setup error (but still refuses setup newer
  than Chitty); the branch gets the new setup when it merges `main`.
- `chitty run` refreshes setup before choosing a ticket: commits it in the main
  checkout, does nothing in a linked worktree. From a linked worktree it refuses
  when the main checkout's setup is older or unrecorded.
- A Chitty older than the recorded setup refuses writes.

## `chitty import backlog-md`

- One-way, from a Backlog.md `backlog/` directory. Never prompts.
- Refuses before writing unless the working tree is clean, untracked files
  included: Git history is the safety net.
- Duplicates are worse than deletion, so it `git rm`s each converted file in
  the import's commit. `--keep-source` keeps them.
- `backlog/config.yml` is consumed and removed under the same rules. Its
  declared statuses map to `backlog`, with one summary line each; only
  undeclared statuses are reported as unknown.
- Other non-ticket files stay and are reported. `backlog/` goes only if empty.
