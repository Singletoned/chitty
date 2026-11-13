## Set up `chitty run`

You are helping a person configure Chitty to run coding agents on tickets. This
is repository setup, not ticket work: make setup changes in the **main checkout**,
never in a ticket worktree or ticket branch. Do not edit a ticket's files to
configure the runner.

1. From the main checkout, run `chitty init` if the repository is not initialized.
   If using Pi, ensure its agent directory (`~/.pi/agent/`, or
   `PI_CODING_AGENT_DIR`) exists first: Chitty installs the extension there only
   when that directory exists. For a clean Git tree, `chitty init --autocommit`
   also enables autocommit and commits the setup files it changes. On an
   existing repository, inspect its configuration before changing it; use
   `chitty init` from main to refresh outdated setup. Do not run init on a
   ticket branch.
2. Edit the existing repository-root `chitty.toml`, or `[tool.chitty]` in the
   root `pyproject.toml` if that is where this repository stores Chitty settings.
   Never create both. Put root settings before the first TOML table in
   `chitty.toml`, or directly under `[tool.chitty]` in `pyproject.toml`:

   ```toml
   autocommit = true
   setup = "make install"
   check = "make check"
   agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"
   ```

   Use this repository's actual worktree setup and validation commands instead
   of the `make` examples. `setup` prepares each ticket worktree; `check`
   validates it before an agent starts. Commands are parsed into arguments,
   not run through a shell. `autocommit = true`, `setup`, and `check` are required.
   A default `agent_command` is required unless the run selects a named command
   from `[agent_commands]` (or `[tool.chitty.agent_commands]` in `pyproject.toml`)
   with `chitty run --agent NAME`. Whichever command is selected must contain
   both `{mode}` and `{id}`, or `{prompt}` as one argument.
3. For Pi, `chitty init` creates the `extensions/` directory and installs the
   shipped Chitty extension when the Pi agent directory exists. Reload or
   restart Pi after installation. Use the Pi command above with that extension;
   `--chitty-{mode}` starts its work or review flow.
   For another agent, configure a command and a way to pass Chitty's role
   instructions, such as its prompt argument with `{prompt}`. Run work and
   review under distinct agent identities; a worker must not review its own
   ticket. Recoverable runner failures enter `error`; a stronger repair agent
   can process them with `chitty run --errors --agent NAME`.
4. Check the config and Git changes in the main checkout, and commit any manual
   configuration changes. When ready to start an agent, use an actual eligible
   ticket, for example `chitty run --ticket ID`, or choose an agent with
   `chitty run --agent NAME`. This starts a real session; it is not a dry run.
   A successful run changes the ticket's status; a run with no eligible ticket
   exits 3. Ticket-scoped failures become `error` tickets for an explicit repair
   run. If a command fails before a safe ticket handoff, fix the reported setup
   or configuration error before retrying; configured `error_reporter` commands
   can send catastrophic failures to systems such as Sump. `chitty run` creates the ticket worktree and runs setup and
   checks there; the agent should not configure Chitty inside it. Before
   declaring the runner ready, run the configured `setup` and `check` commands
   in a throwaway detached worktree (`git worktree add --detach`), without
   `chitty run`, then remove it.

   In a new repository where the first ticket creates the real setup and check
   targets, commit placeholder targets that only print a message; have that
   ticket replace them.
