# CLI

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
                 [--owner X] [--depends-on ID]... [--note TEXT] [--note-file F]
chitty list [-c CTX]... [-s STATUS]... [-l LABEL]... [--owner X] [--search TEXT]
                 [--all]
chitty show ID
chitty edit ID [--title T] [-s STATUS] [--add-label L]... [--rm-label L]... [-p PRIO]
                 [--owner X] [--depends-on ID]... [--rm-depends-on ID]...
                 [-d TEXT | --description-file F] [--replace-in-description OLD NEW]
                 [--ac TEXT]... [--set-ac N TEXT]... [--rm-ac N]... [--check N]... [--uncheck N]...
                 [--plan TEXT | --plan-file F] [--note TEXT] [--note-file F]
                 [--set-notes TEXT | --set-notes-file F]
chitty move ID CTX                 CTX must be in this repo; new ID, sets moved_from
chitty renumber PATH               one of several files sharing an ID gets the next number
chitty archive [ID]                  omit ID to archive every done task
chitty check [-c CTX] [PATH]...    validate; non-zero on any error
chitty fix [-c CTX] [PATH]...      repair safe problems; fail if any remain
chitty path ID                     print the file path (for editors/agents)
chitty guide [setup|work|review|plan|cold-read] [ID]  print agent instructions; setup explains run configuration
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
  Human-readable rows show statuses as a glyph and at most five letters:
  `💤 bklog`, `📝 plan`, `🔎 cold`, `📋 todo`, `🔨 doing`, `⛔ blckd`, `👀 revw`, and
  `✅ done`, and
  priorities as `⬆️` high, `⏺️` medium, `⬇️` low, or blank when unset. Titles are
  cut with `…` so each row fits in `list_width` terminal columns, counting
  emoji as two; labels are kept whole. Rows skipped by `next`
  show the reason's glyph alone in a column before the title (`👤`, `🔒`, `▶`, or
  `⚠️`, whose message goes to stderr); the column appears only when a row needs
  it. Rows do not show the branch. JSON keeps status words and adds `skipped`,
  the full reason: `👤 human`, `🔒 waits on ID[, ID...]`, or `⚠️ <message>`.
- Notes can be appended with `--note` or `--note-file`, or replaced with
  `--set-notes` or `--set-notes-file`; empty replacement removes the section.
  Replacement cannot be combined with append and is not allowed in review.
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
- `list` reads only non-archived tasks: by default it selects `planning`,
  `cold-read`, `todo`, `doing`, `blocked`, and `review` tasks from every context; repeat `-c` to narrow contexts
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
