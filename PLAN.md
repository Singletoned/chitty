# Chitty — plan

Markdown-native task tracker for repos worked on by humans and coding agents.
A clean-room reimplementation of the idea behind Backlog.md, in Python, with
a file format that ordinary markdown tooling leaves alone and a much smaller
surface area.

Put in a chitty; an agent (or you) picks it up; the file is the record.

## Principles

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
  than Chitty), and the branch picks up the new setup when rebased onto `main`.
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

## Non-goals

TUI. Web UI. Cross-branch task resolution. File locking. Format migrations.
Remote/HTTP contexts (sync a directory instead). Subtask IDs (`24.1`).
Milestones. Docs/decisions directories. Wizards. Shell completions (v1).
Configurable statuses (v1). Moving tasks between repos. ID collision
handling beyond reporting it.

## Layout

```
repo/
  chitty.toml
  chitty/
    tasks/                 default context
      TASK-2--add-search.md
      TASK-3--fix-login.md
      archive/
        TASK-1--bootstrap.md
    human/                 another context
      HUMAN-1--rotate-prod-password.md
```

`chitty/` is the backlog root; each context is a subdirectory. Archived
tasks move to `<context>/archive/`. Nothing else lives under `chitty/`.

A missing context directory is an empty context; it is created on first
write. `init` creates `chitty/tasks/` only; `chitty/human/` appears the first
time something is added to it. (Git doesn't track empty directories, so a
freshly cloned repo may have none of them.)

Root discovery (CLI and MCP alike): `CHITTY_ROOT` if set, otherwise walk up
from the current directory to the first directory containing `chitty.toml` or a
`[tool.chitty]` table in `pyproject.toml`. A repo cannot define both sources;
that ambiguity is an error. Error if neither finds one.

## IDs

`<PREFIX>-<n>`, e.g. `TASK-13`.

- `PREFIX` is the context's prefix: `[A-Z]+`, unique within a repo.
  Prefixes name queues (`TASK` for `tasks/`, `HUMAN` for `human/`), not
  projects or types: a ticket's project is the repo it lives in, and its
  type (bug, suggestion) can change while its ID must not, so type is a
  label. New repos always get `TASK`; existing custom prefixes keep working.
- `n` is a positive integer, unpadded: one above the highest number in
  committed ticket files on all local and remote-tracking branches, in the
  context's active or archive directory, plus uncommitted files in this
  checkout. Uncommitted tickets in other worktrees and unpushed work on other
  machines are not visible.
- A context with `random_ids = true` instead draws `n` at random from
  10000000 to 99999999, such as `BACKLOG-48213907`, retrying (a bounded number
  of times, then failing) when a number in that same visible set is taken.
  Random IDs let tickets raised on any branch avoid colliding, so only `main`
  hands out sequential numbers (decided 2026-11-05). The generated `backlog`
  context (`chitty/backlog/`, prefix `BACKLOG`) uses it; it is unrelated to the
  `backlog` status. Plain `chitty add` in a linked worktree targets this context
  so unrelated branch discoveries are filed for planning; explicit contexts
  still win, and inbox pulls use the default context.

Filename: `<ID>--<slug>.md`, or `<ID>.md` when the slug is empty. The slug
is derived from the title (lowercase, `[a-z0-9-]`, collapsed hyphens, max 60
chars; empty if the title has no ASCII alphanumerics) and follows it:
`edit --title` renames the file (`git mv` when tracked), and `chitty fix`
renames files whose slug has gone stale. It is there so `ls` is readable; the
ID is the identity, so renames never break references. Slugs never contain `--`, so the ID is everything before the
first `--`. The ID is not repeated in frontmatter.

Collisions: allocation counts committed ticket files on all local and
remote-tracking branches, in active and archive directories, so branches get
separate IDs. It does not see uncommitted tickets in other worktrees or
unpushed work on other machines; those can still collide. If a collision does
occur, `chitty check` reports the files involved; the human renames one and
fixes references by hand. Likewise, moving the highest-numbered task out of a
context lets its number be reused; accepted.

Referencing: commands accept `TASK-13`, or bare `13` for the default
context. Stored references (`depends_on`, `moved_from`) are always the full
`PREFIX-n` form; shorthand is expanded before writing.

## Task file

```markdown
---
title: Add search to the task list
status: todo
labels:
  - search
  - cli
priority: medium
owner: ed
depends_on:
  - TASK-7
  - HUMAN-1
created: 2026-10-23
---

## Description

Free markdown.

## Acceptance Criteria

- [ ] `chitty list --search` matches title and body
- [x] Matching is case-insensitive

## Plan

Free markdown, written by the agent before implementing.

## Notes

Free markdown. Append-only by convention; not enforced.

## History

- 2026-10-23 → todo
- 2026-10-28T14:03:05Z lively-otter todo → doing
```

`History` is tool-managed, always last, and records every deliberate change:

- Creation by `add`, `suggest` or inbox pull writes
  `- YYYY-MM-DDTHH:MM:SSZ actor → status`, with a UTC timestamp and the
  creating actor.
- An import keeps the source's creation entry, which may be the legacy
  date-only `- YYYY-MM-DD → status` form, and appends
  `- YYYY-MM-DDTHH:MM:SSZ actor: imported task`.
- A status change, archive or restore appends
  `- YYYY-MM-DDTHH:MM:SSZ actor old → new`.
- An `edit` that changes anything other than status appends one event,
  `- YYYY-MM-DDTHH:MM:SSZ actor: action; action`, naming what changed, for
  example `changed priority, notes; wrote the plan; ticked acceptance
  criteria`. Review independence reads `wrote the plan` and `ticked acceptance
  criteria` from these events. An `edit` that changes nothing writes nothing.

Not recorded: rewriting references in other tasks after a move, rename or
delete, `chitty fix` repairs, and `delete`, which removes the task and its
History. Existing date-only entries remain valid.

Frontmatter schema (strict: unknown keys are an error):

| key          | type               | required | notes                                        |
|--------------|--------------------|----------|----------------------------------------------|
| `title`      | string             | yes      | non-empty, single line                       |
| `status`     | `backlog\|todo\|doing\|blocked\|review\|done` | yes     | fixed in v1; backlog needs refinement; blocked needs a reason |
| `labels`     | list[string]       | no       | absent ≡ `[]`                                |
| `priority`   | `low\|medium\|high` | no      | absent means unset                           |
| `owner`      | string             | no       | free text; `human`, a name, an agent         |
| `depends_on` | list[ID]           | no       | any context in the same repo                 |
| `created`    | date               | yes      | ISO 8601 date, set once                      |
| `moved_from` | ID                 | no       | set by `move`; the ID in the source context  |

An owner reserves work tickets for that agent. Plain `chitty next` and
`chitty run` select unowned `todo`/`doing` tickets, but still select owned
`review` tickets unless the owner is `human`; `--owner NAME` selects only that
agent's tickets in any active status. Empty and `human` owner filters are
refused. Explicit `chitty run --ticket ID` ignores non-human ownership.

There is no `updated` field. Git records when a file changed; the field would
add a line to every diff and conflict on every merge.

YAML is loaded with every scalar as a string (no implicit typing), so
`owner: no` is the string `"no"` and `status: on` fails validation as an
unknown status rather than becoming `True`. Pydantic parses `created` from
the string. When the tool *writes* a free-text field (`title`, `owner`,
`labels`) it quotes anything YAML 1.1 or 1.2 would read as a non-string
(`"no"`, `"2026-10-23"`, `"1e3"`), because other tools reading the file
won't be as careful. `created` is a real date and is written unquoted.

Body rules:

- Sections are `##` headings. Recognised: `Description`, `Acceptance
  Criteria`, `Plan`, `Notes`, `Summary`, `History`. `History` is last and
  contains only tool-written status entries. Unrecognised `##` headings, any `#` heading,
  and non-blank content before the first `##` are errors. Use `###` and below
  inside a section for structure.
- The parser is fence-aware: `##` inside a fenced code block is not a heading.
- `Description` is required and non-empty.
- `Acceptance Criteria` contains only a flat task list. An item starts with
  `- [ ]`, `- [x]` or `- [X]` at column 0 and may continue on following
  indented lines (formatters wrap long items). Blank lines between items are
  allowed. Nested lists, unindented prose, and anything else in the section
  are errors. Each item is one criterion, addressed by 1-based position in
  the CLI; no numbers are stored in the text. The tool writes `- [x]`.
- Everything else is free markdown.

### Supported formatters

The round-trip guarantee is tested against, and only claimed for:

- `prettier` with default settings, and with `proseWrap: always`;
- `mdformat` with the `mdformat-gfm` and `mdformat-frontmatter` plugins
  (plain CommonMark mdformat turns `---` into a heading and escapes `[ ]`).

Both are pinned to exact versions. If either is missing, the round-trip
tests fail loudly; they are never skipped.

"Survives" means the file still parses to the same task. Byte-for-byte
no-op is only claimed for ordinary content: `mdformat-frontmatter`
re-serialises YAML as 1.2 and drops the quotes the tool adds for 1.1
readers (`"no"` becomes `no`), and mdformat renumbers ordered lists in free
markdown.

### Writing

Serialisation is a patch over the original text, not parse-then-dump:

- Frontmatter is split into one span per top-level key (the key's line plus
  any indented lines under it). Changed keys have their span replaced, new
  keys are appended in table order, removed keys have their span deleted.
  Every other byte — comments, quoting, blank lines — is left alone.
  Comment and blank lines belong to the key below them, so replacing a key
  keeps the comment above it.
- The body is split the same way, one span per `##` section. Only sections
  the command changed are rewritten; new sections are appended in the
  canonical order above.
- Acceptance Criteria are patched per item, so formatter wrapping survives:
  `--check`/`--uncheck` change only the bracket character, `--rm-ac`
  deletes that item's lines, `--ac` appends one line.
- Lists are written block-style (one item per line). Flow style is accepted
  on read and left alone if the key isn't being changed.
- If the resulting content equals the current content, the file is not
  written.
- `--note TEXT` appends `TEXT` as a new paragraph (preceded by a blank line)
  to `## Notes`, creating the section if absent. No date prefix; include one
  in the text if you want it.
- Creating a task writes an actor-attributed UTC initial History transition.
  A changed `--status`, archiving, and restoring append a transition; a no-op
  status edit does not. Every other `edit` that changes the task appends one
  actor-attributed event naming the changed fields, notes, plan or criteria.
  Imports retain their source creation entry and append an import event; safe
  `fix` repairs, `delete`, and reference rewrites in other tasks append none.
- All checklist indices in a single `edit` refer to the list as it was
  before the command ran. `show` prints the numbers next to each criterion so
  callers don't count.

## Config

Repository config is either `chitty.toml` at repo root (`chitty init` writes it)
or a `[tool.chitty]` table in `pyproject.toml`; defining both is an error. Unknown
configuration keys are ignored with a warning.

```toml
format = 1
default_context = "tasks"
chitty_version = "0.1.2" # written by init; warns when setup is stale
autocommit = false # if true, commit each write; `chitty init --autocommit` enables it and commits setup
review = true # require review before done
# autoformat = "taidy format" # run on every written task file
# setup = "make install" # run in every ticket worktree before the agent starts
# agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"
# `{prompt}` may be used as one argument containing `chitty guide` output.
archive = "move" # or "delete"; retain completed files or delete them

[contexts.tasks]
prefix = "TASK"

[contexts.human]
prefix = "HUMAN"
review = false # overrides the repository default

[contexts.backlog]
prefix = "BACKLOG"
random_ids = true # random eight-digit numbers instead of sequential ones

[agent_commands]
# Other parsed agent commands, selected for one run with `chitty run --agent NAME`.
```

Context directory is `chitty/<name>/`. Not configurable. `review` defaults to
`true`; with it enabled, only `review → done` can complete a task. A context
can set `review` to override the repository default; an absent context setting
inherits it. New `human` contexts disable review so people can close their own
tasks directly.

`chitty init` adds the `backlog` context to an existing repository, as a
table after the last `[contexts.*]` (or `[tool.chitty.contexts.*]`) table. It
leaves the file alone when a `backlog` context or a `BACKLOG` prefix already
exists, when contexts have no table header to follow (dotted keys or inline
tables), or when the result would not validate. An older Chitty refuses a
context with `random_ids`; `chitty_version` already says it needs upgrading.

Agents reviewing each other's work can fail a task back and forth without
converging. The third `review → doing` since the task was last `blocked` is
applied as `review → blocked` with owner `human` and a note giving the count,
alongside the reviewer's own note. Unblocking starts the count again. The
limit is `REVIEW_FAILURE_LIMIT` in `store.py`, not configuration, until a
repository needs a different one.

When set, `autoformat` is parsed without a shell and run on existing files
written by each operation. The order is `fix`, `autoformat`, then `autocommit`;
unresolved fixes prevent the latter two steps. `archive = "move"` is the
standard retention policy. With `archive = "delete"`, archive deletes done
files and strips exact `depends_on` entries elsewhere; ID allocation reads Git
deletions (including uncommitted ones), and fails rather than guessing if the
repository history is shallow or unavailable.

Contexts are repository-local. To send a task to another repository, use
`chitty suggest PROJECT TITLE`; the receiving repository imports its machine-local
inbox with `chitty inbox --pull`. This avoids writing another repository's worktree.
`PROJECT` is a registered project name, which always wins; it is read as a
path only when it contains `/`, is `.`, or starts with `~` or `.`, because
every repository has a `chitty/` folder that a bare name would otherwise hit.

## Dependencies

`depends_on` may reference any context in the same repo (`TASK-3` blocked on
`HUMAN-1` is the common case). Rules:

- A reference to an ID that doesn't exist in the repo is a `check` error.
- A reference to an archived task is fine; archived is not deleted.
- `move` gives the task a new ID in the target context and rewrites every
  reference to the old ID across the repo, reporting which files it touched.
- User-level contexts are write targets only; nothing can depend on a task
  in another repo. If you need to track it, write the foreign ID in your own
  task's Notes.

## CLI

All commands take `--json` on reads (and on writes, printing the resulting
task). Exit non-zero with a message on stderr for every error. No prompts,
no wizards; every command is fully specifiable by flags. Click's standard bash
and zsh completion exposes commands/options; task ID and context completion is
repository-aware and silently empty outside a repository.

```
chitty init [--autocommit]         write chitty.toml, chitty/tasks/, AGENTS.md block, CLAUDE.md symlink; `--autocommit` requires a clean Git tree
chitty inbox [--pull]              list waiting suggestions, or print actor then import them all
chitty whoami                       print the stable actor name for this session
chitty add TITLE [-d TEXT] [-s STATUS] [-c CTX] [--ac TEXT]... [-l LABEL]... [-p PRIO]
                 [--owner X] [--depends-on ID]...
chitty list [-c CTX]... [-s STATUS]... [-l LABEL]... [--owner X] [--search TEXT]
                 [--all]
chitty show ID
chitty edit ID [--title T] [-s STATUS] [--add-label L]... [--rm-label L]... [-p PRIO]
                 [--owner X] [--depends-on ID]... [--rm-depends-on ID]...
                 [-d TEXT | --description-file F]
                 [--ac TEXT]... [--rm-ac N]... [--check N]... [--uncheck N]...
                 [--plan TEXT | --plan-file F] [--note TEXT]
chitty move ID CTX                 CTX must be in this repo; new ID, sets moved_from
chitty renumber PATH               one of several files sharing an ID gets the next number
chitty archive [ID]                  omit ID to archive every done task
chitty check [-c CTX] [PATH]...    validate; non-zero on any error
chitty fix [-c CTX] [PATH]...      repair safe problems; fail if any remain
chitty path ID                     print the file path (for editors/agents)
chitty guide                       print the agent instructions (the AGENTS.md block)
chitty mcp                         stdio MCP server (needs the mcp extra)
```

- `-c/--context` defaults to `default_context`. On `add`, a user-level
  context name is accepted: the file is written into that repo's working
  tree as an untracked file and nothing else happens there — no commit,
  pull or push, and that repo's `autocommit` setting is ignored. Any
  `--depends-on` is validated against the *target* repo. Post-and-forget.
  On every other command, `-c` must name a context in this repo.
- `renumber` repairs two files sharing an ID, as a merge of two branches that
  each added a ticket can leave. Such files collapse into one ticket for `show`,
  `edit` and `list`, so it takes the path of the file to change, found through
  `scan`, and refuses a path that is not a task file in a context, or whose ID
  no other file uses (`move` covers ordinary moves). The file keeps its slug,
  gets the next number in its context and records `moved_from`. References are
  never rewritten, because a `depends_on` or `parent` naming a shared ID cannot
  say which file it meant, and `check` cannot catch a wrong one since the old ID
  still resolves; instead it lists every ticket naming the old ID for a person
  to check.
- `-d` is required on `add` except with `-s backlog`, which writes the default
  required Description: `This ticket needs refining.`
- `list` includes a priority column only when a listed task has a priority.
  It orders the selected statuses first, then `high`, `medium` (including
  unset priority), and `low` within each status; `--json` uses the same order.
  Human-readable rows prefix statuses with fixed glyphs: `💤 backlog`, `📋 todo`,
  `🔨 doing`, `⛔ blocked`, `👀 review`, and `✅ done`. Rows skipped by `next`
  end with `👤 human`, `🔒 waits on ID[, ID...]`, or `⚠️ <message>` for a broken
  dependency. JSON keeps status words and adds `skipped`.
- `Summary` is an optional final handoff section after Notes; set it with
  `edit --summary` when completing work.
- `parent` is an optional full task ID for grouping flat tasks. `add` and
  `edit` expand shorthand IDs; `list --parent ID` filters direct children and
  `show` lists them. Parents must exist and cannot form cycles.
- `ID` arguments accept `TASK-13` in any case, or bare `13` for the default
  context. IDs are canonicalised to upper-case for output and writes; `check`
  reports legacy non-upper-case `depends_on` entries and `fix` rewrites them.
- `check` is read-only and reports errors and warnings. Errors make it exit
  non-zero; warnings are advisory and do not affect its exit status. `fix`
  applies safe repairs, reports remaining diagnostics, and exits non-zero only
  when errors remain. It never rewrites warning-only Markdown; use backticks
  when literal Markdown delimiters denote code. Autocommit runs it on written
  task files first and is blocked only by errors.
- `list` reads only non-archived tasks: by default it selects `todo`, `doing`,
  `blocked`, and `review` tasks from every context; repeat `-c` to narrow contexts
  or `-s` to choose statuses, including `backlog` and `done`. `--all` selects every status
  but still excludes archive folders. An empty list reports its active filters
  on stderr while keeping stdout (including JSON) empty.
  Default output is one line per task:
  `TASK-12  doing   Add search to the task list  [cli,search]`.
- `archive` with no ID processes every non-archived `done` task across contexts
  in one batch; use it when preparing a merge request. `archive = "move"`
  moves files into `archive/` and records `… → archived` in History (the default);
  `archive = "delete"` deletes them (and therefore their History),
  removes exact dependencies elsewhere, and retains their numbers from Git
  history. With an ID it processes one task as before.
- `move` is within the current repo only. It gives the task the next number
  in the target context and keeps the slug. There is no cross-repo move;
  `add -c otherrepo` plus `archive` here is the explicit two-step version.

## MCP

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

## Agent instructions

`chitty init` appends this block to `AGENTS.md` (creating it if absent),
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

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Put paths, globs, commands, IDs and code in backticks in titles, descriptions,
  criteria and notes.
- Work on one task per session. Start with `chitty show <ID>`.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick acceptance criteria as you meet them: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`).
- Record anything surprising with `--note`. Set `-s review` when work is ready.
  Never review a ticket you worked on: review promptly, not at merge-request
  time. Pass with `-s done --note "Reviewed: ..."`; fail with
  `-s doing --note "reason"`. If the work is on a branch, the reviewer who
  passes it merges it into `main` and removes the branch and its worktree.
  Create new tickets for out-of-scope findings.
  The third failed review sets `blocked` and owner `human` instead.
- Set `-s done` when every criterion is ticked and the work is verified.
- End commits for task work with `Task: <ID>` lines, using the ticket's own ID
  (e.g. `Task: TASK-12`), so `git log --grep <ID>` finds a ticket's code.
- Found unrelated work? `chitty add` it (`-c human` if it needs a person).
  Don't do it in this session.
```

That is the whole prompt. Statuses are fixed, so the block is always correct.
`chitty guide` prints the same unmarked block, and `chitty --help` points agents at it.

## Pipeline and feedback

Direction, not current behaviour: TASK-109 pilots this by hand, and TASK-110
builds only what the pilot justifies. Until then the statuses above stand.

```
backlog → design → tests → review-ticket → work → review-work → done
```

| stage           | who                 | leaves when                                                      |
|-----------------|---------------------|------------------------------------------------------------------|
| `design`        | human, strong model | the ticket meets the ready definition and passes a cold read     |
| `tests`         | fresh session       | spec tests are committed and fail for the expected reason        |
| `review-ticket` | human, for now      | the ticket is small and clear, and the tests match it            |
| `work`          | fresh session       | spec tests pass and are unchanged, and `make check` passes       |
| `review-work`   | fresh session       | the diff meets the ticket, judged without the worker's reasoning |

Each stage has a different session, and nobody reviews a stage they did. Any
number of workers and reviewers may run at the same time. `chitty run` takes
a per-ticket lock right after choosing its ticket and holds it until it
returns: an exclusive, non-blocking `flock` on `<git common dir>/chitty/run/<ID>.lock`,
shared by every worktree and never committed. The kernel releases it when the
process exits, so no lock goes stale. `next_action` skips locked tickets, a run
that loses the race chooses again, and `--ticket` refuses a locked ticket. A
committed claim was rejected because a killed run would leave it for a person
to clear; locks are machine-local because Chitty runs on one machine. The
sessions write the main checkout during setup and review merges; a Git
lock or dirty-file collision fails loudly, so rerun the affected session. A
failed review restarts in a fresh session with the finding added as a
criterion. The second failure stops for the human: by then the ticket is the
likely problem. Work and review-work block for a human if the design or tests
are wrong, and never edit the spec tests.

Scripted gates come first because they cost no tokens and cannot be talked
round. They never relax, since trust does not build up in agents: only the
human's sampling rate moves, and only on measured escapes.

Ready definition. A fresh agent can do the ticket and know when to stop, and
another can check the result without talking to the first:

- Criteria are executable: a test or command defines done.
- Scope is stated so a reviewer can reject on it, with an out-of-scope list.
- Decisions are made: no "use your judgement".
- It points at relevant files and patterns instead of pasting them.
- It lists every path or caller the behaviour must hold on.
- It does one thing. Aim for one to three criteria and a diff of a hundred or
  two lines. Five criteria or a few hundred lines is the limit, and reaching it
  is a prompt to split, not to carry on. `TASK-126`, at 16 criteria and about
  1,000 lines, failed six reviews.
- Criteria state behaviour and leave lists of cases to the tests, because a
  listed case can always be read more strictly.

Cold read: an implementing read has a fresh, cheap-model agent implement a code-
changing ticket in a detached worktree and run its tests with and without the
fix; when there is nothing to run, a stronger model reads the ticket and
referenced code instead. Decided with the human (2026-11-05): use a detached
worktree and keep the implementing commit under `refs/cold-read/<ID>/<n>`, not a
branch, because Chitty searches branches for ticket copies and history should
be retained after the worktree is removed. Workers and reviewers do not do it
(2026-11-04: a worker read the procedure in `AGENTS.md` as its own step), so the
procedure is printed for planners:

The complete procedure lives in the planning role instructions printed by
`chitty guide plan`. Keep a new ticket in `backlog` until its cold read findings
have outcomes, and only then move it to `todo`, because `chitty run` picks up
anything in `todo`: `TASK-147` was claimed with a wrong fix while its cold read
was still running.

Spec tests exercise the public surface (CLI, MCP, HTTP, file format), never
private helpers or mocks of our own code. Use a round-trip property for any
parser or serialiser, and a table row for any state transition. They are
written from the ticket, before and without sight of the implementation.

### Feedback loops

Agents do not learn from correction, so a lesson counts only once it changes
something read or run later. In order of preference, that is a mechanical
check, then a template, then a prompt rule. Prompt rules have a fixed budget:
adding one means removing one.

| loop         | sensor                                                  | changes                       |
|--------------|---------------------------------------------------------|-------------------------------|
| ticket       | cold-read mismatch; predicted versus changed files      | the ticket, before work       |
| failure      | each failure's cause, and whether it cited a criterion  | standing rules, or the ticket |
| escape       | later bugs linked to their source; sampled audits       | gates and sampling rate       |
| test strength | occasional mutation runs                               | survivors become tickets      |
| replay       | past work stages rerun against their spec tests         | prompt and model choices      |

A failure's cause is the earliest stage that should have caught it: `design`,
`tests`, `work`, `integration` (branch, merge, environment) or `review` (the
reviewer was wrong). Record it as `Review failed (<cause>): ...`. A later bug
gets the label `escape` and a note naming its source ticket.

A retro is a ticket, opened after every 10 `done` tickets. It proposes a few
changes, each naming the failure class it should reduce, and the human accepts
or rejects them. An audit samples 1 in 5 `done` tickets. Both frequencies are
starting points, limited by the human's time.

Agents never see these metrics. First-pass yield also rises if reviewers go
soft, so it is only read alongside escapes. Judge cost per accepted ticket,
including retries, not per run.

## Stack

- Python ≥ 3.12, packaged with `uv`; installed as `uv tool install chitty`,
  tried with `uvx chitty`.
- On a machine developing Chitty, the global `chitty` is an editable install of
  the main checkout (reverses `TASK-81`, see `TASK-118`). Work happens in
  worktrees, so `main` should always be safe, and if it is not that needs fixing
  anyway. It also means a version bump on `main` needs no release before `chitty`
  can write to this repository. There is no shared virtual environment: each
  checkout has its own `.venv`, used through `make` and `uv run`.
- Runtime: `click`, `pydantic`, `pyyaml`. Frontmatter is split on `---` by
  our own code; YAML is loaded with a loader that resolves every scalar as a
  string. Optional extra `mcp`.
- Dev: `ruff`, `pyright` (strict for `src/`, standard for tests; with
  `types-PyYAML`), `unittest` (stdlib;
  tests write real files in a temp dir and drive the CLI through
  `click.testing.CliRunner`; no filesystem mocking), `prettier` and `mdformat`
  with the plugins above for the round-trip tests.
- `Makefile` following the mate conventions (`.PHONY` targets with `##`
  descriptions): `make check` (ruff + pyright + tests), `make format`.
- Git via `subprocess.run(..., check=True)`. `chitty init --autocommit` first
  requires a clean tree, enables `autocommit`, then commits only setup files it
  changed with `chitty: initialize and enable autocommit`. For task writes when
  `autocommit` is on: `git add -- <paths> && git commit --only -m "chitty: <verb> <ID> <title>\n\nTask: <ID>" -- <paths>`,
  with one `Task: <ID>` trailer for every task the commit writes. All affected
  paths are listed (two for `move`/`archive`, more when `move` rewrites
  references), so nothing the user had staged is swept in. Failure is a loud
  error.

## Next action and runner

`chitty next` selects one active task across every context: `review` before
`doing` before `todo`, then high/medium (including unset)/low priority and
`TaskId`.
Human-context tasks and tasks owned by `human` are excluded. A `todo` task with
an unmet dependency is excluded, while `doing` and `review` work remains
visible. `list` reports these exclusions with `👤 human`, `🔒 waits on ID[, ID...]`,
or `⚠️ <message>` for a broken dependency; `doing` and `review` ignore
dependencies. It prints `work ID` or `review ID`; `--json` and the read-only MCP
`next` tool return the same `{mode, id}` value. `--mode review` limits the
choice to `review` tasks and `--mode work` to `doing` and `todo`, in the same
order, filtering before dependencies are checked so a bad reference on a task
in the other mode does not stop this one. With nothing left it prints `no next
ticket` (or `no next ticket for --mode MODE`) to stderr and exits 3, a status of
its own, so an idle reviewer is distinguishable from a broken one, which exits
1. An idle queue includes one where every `todo` task waits on a dependency.
`chitty run` exits 3 in the same case. The MCP tool keeps the default.

`chitty run` requires `autocommit = true`, a configured `setup` command, and
an `agent_command`, unless `--agent NAME` selects an entry from `[agent_commands]`.
Use `chitty run --ticket ID` to choose a ticket instead of using the next selected ticket. A plain run skips owned `todo` and `doing` tickets, while still selecting owned `review` tickets; use `--owner NAME` to select that agent's tickets at any active status. `--owner human` and an empty owner are refused, as is combining `--owner` with `--ticket`.
`chitty run --mode MODE` selects as `chitty next --mode MODE` does, and is
refused with `--ticket` before anything else runs, because the ticket already
decides its mode.
The command may include `{prompt}` as a single argument;
Chitty fills it with the role-specific `chitty guide <mode> <ID>` output after
splitting the command. It finds the main checkout even when invoked from another
worktree, creates or reuses the selected
ticket's worktree, runs parsed setup there, and claims a `todo` work ticket on
that branch before launching the parsed agent command. The command must include
`{mode}` and `{id}`, unless it includes `{prompt}`; Chitty replaces them after
splitting, and arguments after
`--` pass through to the agent. It reopens the ticket worktree after the agent
exits and succeeds only if the task's committed status changed. This makes
`while chitty run; do :; done` a safe unattended loop that stops when the queue
is empty. To wait out an idle queue instead, treat exit 3 as success:
`while chitty run --mode review || [ $? -eq 3 ]; do sleep 60; done` runs until
something fails. `chitty run` checks its configuration, refreshes setup
before selecting, so each idle pass does that, and a broken
configuration exits 1, not 3. An agent's or setup's own exit status always
surfaces as 1. Interrupting setup or the agent exits 130 without a traceback.

Before a review (decided with the human, 2026-11-03), after the run's actor is
set, `chitty run` prepares the ticket's worktree so the reviewer sees exactly
what would land, keeping `main` linear:

1. A rebase left unfinished, for example by a crash, is a loud error for the
   human, with no status change.
2. Uncommitted changes, including untracked but not ignored files, move the
   ticket to `doing` with `Review failed (work): ...` listing them.
3. It rebases the branch onto the local `main`. On a conflict it runs
   `git rebase --abort` and moves the ticket to `doing` with `Review failed
   (integration): ...` naming the conflicting files, for the worker to resolve
   in a fresh session. The rebase runs with `rerere.enabled=false`, so a
   resolution Git recorded for another branch is never replayed unchecked.
4. Only then does `setup` run, because the rebase can change dependencies. In
   work mode `setup` still runs before the claim.

After either failure no agent starts, no usage line is written, and `chitty
run` exits 0 because the status changed, printing the change. The moves go
through `Repo.edit` under the run's own actor, which never worked on the
ticket, so they count with reviewers' failures towards `REVIEW_FAILURE_LIMIT`.
Interrupting the rebase aborts it and exits 130. A clean rebase is not
repeated or re-reviewed if `main` moves during the review; landing is
`TASK-131`.

Each agent session appends one JSON line to the machine-local usage log at
`$XDG_DATA_HOME/chitty/usage/<project>.jsonl` (or the platform data directory
when `XDG_DATA_HOME` is unset). The line records the ticket, mode, actor,
start time, elapsed seconds, statuses, and the Pi session's aggregate token and
cost totals by provider and model. The cost values are provider list prices,
not an invoice or a negotiated rate. A real scratch-repository Pi session was
checked against its session JSONL: the log and session file both reported
`input=7645`, `output=917`, `cacheRead=32000`, `cacheWrite=0`, and
`cost=0.0032694` (0% difference).

## Module layout

```
src/chitty/
  __init__.py
  model.py       Task, Frontmatter, Criterion — parse/validate/serialise ONE file
  ids.py         ID and filename parsing, slugs, next number, shorthand
  config.py      RepoConfig, UserContexts — load + validate TOML
  actor.py       stable actor names from harness session identities
  store.py       Context, find/list/read/write/move/archive
  check.py       cross-file validation: parse errors, duplicate IDs,
                 dangling or self depends_on
  errors.py      ChittyError, the base of every user-facing error
  git.py         optional autocommit
  run.py         Pi subprocess runner for `chitty run`
  cli.py         click commands; thin, calls store/model, prints
  mcp.py         tool definitions wrapping the same functions as cli.py
                 (mcp ≥ 2: MCPServer, not FastMCP)
  guide.md       the AGENTS.md block, as package data
  roles/         work, review, and planning instructions, as package data
```

`cli.py` and `mcp.py` contain no logic; both call the same functions in
`store.py`/`model.py` so behaviour cannot diverge. Actor identity comes from
`CHITTY_ACTOR` or a supported harness session variable. Chitty's Pi extension
copies the session ID into `CHITTY_PI_SESSION_ID` at session start, which takes
precedence over Pi's shell-only variable so descendants retain their parent's
identity. context-mode's server starts at `before_agent_start`, after that,
so its commands inherit the variable. Only a server started before
`session_start` needs the `CHITTY_ACTOR` workaround.

## Build order

1. `model.py` + `ids.py` + tests: parse, single-file validation, patch-style
   serialisation, round-trip. Tests include: prettier (default and
   `proseWrap: always`) and mdformat (with plugins) are no-ops on tool
   output; a wrapped criterion is one criterion and ticking it doesn't
   unwrap it.
2. `config.py`, `store.py`: contexts, read/write/move/archive,
   missing-directory-is-empty.
3. `check.py`: duplicates and dangling references.
4. `cli.py`: `init`, `add`, `list`, `show`, `edit`, `check`, `path`.
5. `move`, `archive`, user-level contexts.
6. `autocommit`.
7. `mcp.py` as the optional extra.
8. Dogfood: track Chitty's own work in `chitty/` from step 4 onward.

Steps 1–4 are a usable tool. Estimate for the whole list: 3–5k lines
including tests.
