# Principles

- The files are the truth. No database, no index, no cache. A directory scan
  is fast enough for thousands of tasks.
- One task, one file, one writer at a time. No locking or automatic conflict
  repair. Task reads use committed state from every local and remote-tracking
  Git branch, selecting each task's most recently changed version; uncommitted
  files in the current worktree override that state. A write refuses when the
  latest committed version is on another branch, directing the caller to its
  worktree or checkout; it never routes writes across branches. Worktrees must
  therefore use `autocommit = true` (or commit every Chitty write) so other
  branches can see their task state. IDs are sequential; task creation is expected to be
  centralised (one agent or human), so we assume parallel branches don't
  collide. `check` reports it if they do.
- Simple first. Add complexity when real-world use shows it is needed, not
  before.
- Each repository has a validated lowercase `project` name. `init` registers
  its machine-local inbox under XDG data storage and refuses a name owned by a
  different repository. `suggest` writes atomic cross-project ideas there;
  `inbox` lists waiting suggestions without changing anything; `inbox --pull`
  converts them into backlog tasks at session start (`pull` only says to run
  `inbox --pull`).
  User-level contexts are ignored; use `suggest` for cross-project ideas.
- Plain markdown. Every file must survive a round trip through the supported
  formatters (below) without changing meaning. No HTML comments, no sentinel
  markers, no numbering inside checklist text.
- Loud errors. Malformed files are rejected with a path and a reason, never
  silently repaired. `chitty check` is the compile step.
- Chitty does the bookkeeping. Anything the tool can work out or keep
  consistent itself (status that follows from other fields, references to
  finished tasks, dates, who did what) it does automatically, rather than
  asking agents to remember. Agent instructions are for judgement, not
  upkeep. This covers workflow steps too: whatever a script can do reliably
  (creating branches and worktrees, setup, claiming, merging) `chitty run`
  does, and the agent is told only about what is left. Chitty never calls a
  model: models sit only in the worker and reviewer seats. Which agent sits
  there is configuration, not design: Pi is today's choice, and token
  efficiency may change it, so agent-specific code stays in integrations.
- The tool carries the rules, not a prompt. Validation and `--help` are the
  documentation; the agent instructions are ~20 lines and static.
- Minimal diffs. The tool never touches a line it didn't change, and never
  writes a file whose content would be unchanged. `init` is idempotent: it
  adds missing setup only and refreshes the managed agent-guide block.
- `chitty init` is the idempotent setup and format-migration path. It installs
  the machine-wide Pi extension only from a main Git checkout; linked worktrees
  skip all machine-wide Pi setup. Non-Git directories remain eligible to install
  it. Reads work
  with an older setup; writes require it to be current. With `autocommit =
  true`, Chitty upgrades and commits setup separately before the requested
  write; otherwise it fails loudly and tells the caller to run `chitty init`.
  Upgrades happen only in the main checkout: a write in a linked worktree
  skips the upgrade and the stale-setup error (still refusing a setup newer
  than Chitty), and the branch picks up the new setup when merged with `main`.
  `chitty run` refreshes setup before selecting a ticket, committing setup-only
  changes in a main checkout and doing nothing in a linked worktree. From a
  linked worktree, it refuses to run when the main checkout's setup is older or
  unrecorded; run it from the main checkout instead. A Chitty version older than
  the recorded setup refuses writes clearly.
  `chitty import backlog-md` is an explicit,
  one-way converter from a Backlog.md `backlog/` directory. Git history is the
  safety net, so it refuses to run, before writing anything, unless the Git
  working tree is clean, untracked files included; that also keeps its
  changes apart from unrelated work. Duplicate tickets are worse than
  deletion, so after a successful import it `git rm`s each converted source
  file in the import's commit; `--keep-source` leaves them instead.
  `backlog/config.yml` is consumed by the import and removed under the same
  rules. Statuses it declares map to `backlog` with one summary line each;
  only undeclared statuses are reported as unknown. Other non-task files stay
  and are reported, and `backlog/` goes only if it ends up empty. It never
  prompts.
