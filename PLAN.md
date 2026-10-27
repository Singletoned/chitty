# Chitty — plan

Markdown-native task tracker for repos worked on by humans and coding agents.
A clean-room reimplementation of the idea behind Backlog.md, in Python, with
a file format that ordinary markdown tooling leaves alone and a much smaller
surface area.

Put in a chitty; an agent (or you) picks it up; the file is the record.

## Principles

- The files are the truth. No database, no index, no cache. A directory scan
  is fast enough for thousands of tasks.
- One task, one file, one writer at a time. No locking, no cross-branch
  scanning, no automatic conflict repair. If you want a task from another
  branch, merge the branch. IDs are sequential; task creation is expected to
  be centralised (one agent or human), so we assume parallel branches don't
  collide. `check` reports it if they do.
- Simple first. Add complexity when real-world use shows it is needed, not
  before.
- Each repository has a validated lowercase `project` name. `init` registers
  its machine-local inbox under XDG data storage and refuses a name owned by a
  different repository. `suggest` writes atomic cross-project ideas there;
  `pull` converts waiting suggestions into backlog tasks at session start.
  User-level contexts are ignored; use `suggest` for cross-project ideas.
- Plain markdown. Every file must survive a round trip through the supported
  formatters (below) without changing meaning. No HTML comments, no sentinel
  markers, no numbering inside checklist text.
- Loud errors. Malformed files are rejected with a path and a reason, never
  silently repaired. `chitty check` is the compile step.
- The tool carries the rules, not a prompt. Validation and `--help` are the
  documentation; the agent instructions are ~20 lines and static.
- Minimal diffs. The tool never touches a line it didn't change, and never
  writes a file whose content would be unchanged. `init` is idempotent: it
  adds missing setup only and refreshes the managed agent-guide block.
- No Chitty-format migrations in v1. `chitty import backlog-md` is an explicit,
  one-way converter from a Backlog.md `backlog/` directory; it leaves source
  files in place for review and deletion by a person.

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
- `n` is a positive integer, unpadded: `max(n over existing files in the
  context, including archive) + 1`.

Filename: `<ID>--<slug>.md`, or `<ID>.md` when the slug is empty. The slug
is derived from the title at creation (lowercase, `[a-z0-9-]`, collapsed
hyphens, max 60 chars; empty if the title has no ASCII alphanumerics) and is
**not** updated when the title changes — it is there so `ls` is readable,
nothing more. Slugs never contain `--`, so the ID is everything before the
first `--`. The ID is not repeated in frontmatter.

Collisions: task creation is expected to be centralised, so two branches
creating the same ID is assumed not to happen in practice. If it does,
`chitty check` reports the files involved; the human renames one and fixes
references by hand. No tooling beyond that until real use shows it's
needed. Likewise, moving the highest-numbered task out of a context lets
its number be reused; accepted.

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
- 2026-10-28 todo → doing
```

`History` is tool-managed, always last, and records task creation plus every
status or archive-state transition. Its entries are `- YYYY-MM-DD old → new`;
the initial entry omits `old`. Deleting a task removes its History with it.

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
- Creating a task writes its initial History entry. A changed `--status`,
  archiving, and restoring append a transition; a no-op status edit does not.
- All checklist indices in a single `edit` refer to the list as it was
  before the command ran. `show` prints the numbers next to each criterion so
  callers don't count.

## Config

Repository config is either `chitty.toml` at repo root (`chitty init` writes it)
or a `[tool.chitty]` table in `pyproject.toml`; defining both is an error:

```toml
format = 1
default_context = "tasks"
autocommit = false                     # if true, commit each write
review = true                          # require review before done
# autoformat = "mdformat"              # command run on every written task file
# archive = "move"                      # or "delete" completed files at merge time

[contexts.tasks]
prefix = "TASK"

[contexts.human]
prefix = "HUMAN"
```

Context directory is `chitty/<name>/`. Not configurable. `review` defaults to
`true`; with it enabled, only `review → done` can complete a task. Set it to
`false` to make review optional.

When set, `autoformat` is parsed without a shell and run on existing files
written by each operation. The order is `fix`, `autoformat`, then `autocommit`;
unresolved fixes prevent the latter two steps. `archive = "move"` is the
standard retention policy. With `archive = "delete"`, archive deletes done
files and strips exact `depends_on` entries elsewhere; ID allocation reads Git
deletions (including uncommitted ones), and fails rather than guessing if the
repository history is shallow or unavailable.

User-level `~/.config/chitty/contexts.toml` (optional), for adding tasks to
other repos or to a personal backlog:

```toml
[contexts.hypurrcube]
repo = "~/src/hypurrcube"        # that repo's chitty.toml applies
context = "tasks"                # optional; default is that repo's default_context

[contexts.improvements]
repo = "~/notes/improvements"    # any directory with a chitty.toml
```

Resolution of a context name: repo `chitty.toml` first, then user file.
A name present in both is an error (no silent shadowing). A name in neither
is an error naming both paths.

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
chitty init [--prefix TASK]        write chitty.toml, chitty/tasks/, AGENTS.md block
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
- `-d` is required on `add` except with `-s backlog`, which writes the default
  required Description: `This ticket needs refining.`
- `Summary` is an optional final handoff section after Notes; set it with
  `edit --summary` when completing work.
- `parent` is an optional full task ID for grouping flat tasks. `add` and
  `edit` expand shorthand IDs; `list --parent ID` filters direct children and
  `show` lists them. Parents must exist and cannot form cycles.
- `ID` arguments accept `TASK-13` in any case, or bare `13` for the default
  context. IDs are canonicalised to upper-case for output and writes; `check`
  reports legacy non-upper-case `depends_on` entries and `fix` rewrites them.
- `check` is read-only. `fix` applies safe repairs, reports each one, and exits
  non-zero if problems remain. Autocommit runs it on written task files first.
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
same names and argument names: `add`, `list`, `show`, `edit`, `note`, `move`,
`archive`, `check`, `fix`, `path`. They return the same JSON
the CLI prints with `--json`. One resource, `chitty://guide`, returning the
same text as the AGENTS.md block. Tool descriptions state the rules (one
task per session, write Plan before coding, tick criteria as you go).

The `mcp` package pulls in starlette, uvicorn, httpx and friends, so it is an
optional extra: `uv tool install 'chitty[mcp]'`. Agents with a shell can use
the CLI with `--json` and need none of it. `chitty mcp` without the extra
exits with an error saying so.

## Agent instructions

`chitty init` appends this block to `AGENTS.md` (creating it if absent),
idempotently, keyed on the `## Chitty` heading:

```markdown
## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Work on one task per session. Start with `chitty show <ID>`.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick acceptance criteria as you meet them: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`).
- Record anything surprising with `--note`. Set `-s review` when work is ready.
  Never review a ticket you worked on: review promptly, not at merge-request
  time. Pass with `-s done --note "Reviewed: ..."`; fail with
  `-s doing --note "reason"`. Create new tickets for out-of-scope findings.
- Set `-s done` when every criterion is ticked and the work is verified.
- Found unrelated work? `chitty add` it (`-c human` if it needs a person).
  Don't do it in this session.
```

That is the whole prompt. Statuses are fixed, so the block is always correct.
`chitty guide` prints the same block, and `chitty --help` points agents at it.

## Stack

- Python ≥ 3.12, packaged with `uv`; installed as `uv tool install chitty`,
  tried with `uvx chitty`.
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
- Git via `subprocess.run(..., check=True)`. Only used when `autocommit` is
  on: `git add -- <paths> && git commit --only -m "chitty: <verb> <ID> <title>" -- <paths>`,
  with all affected paths listed (two for `move`/`archive`, more
  when `move` rewrites references), so nothing the user had staged is swept
  in. Failure is a loud error.

## Module layout

```
src/chitty/
  __init__.py
  model.py       Task, Frontmatter, Criterion — parse/validate/serialise ONE file
  ids.py         ID and filename parsing, slugs, next number, shorthand
  config.py      RepoConfig, UserContexts — load + validate TOML
  store.py       Context, find/list/read/write/move/archive
  check.py       cross-file validation: parse errors, duplicate IDs,
                 dangling or self depends_on
  errors.py      ChittyError, the base of every user-facing error
  git.py         optional autocommit
  cli.py         click commands; thin, calls store/model, prints
  mcp.py         tool definitions wrapping the same functions as cli.py
                 (mcp ≥ 2: MCPServer, not FastMCP)
  guide.md       the AGENTS.md block, as package data
```

`cli.py` and `mcp.py` contain no logic; both call the same functions in
`store.py`/`model.py` so behaviour cannot diverge.

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
