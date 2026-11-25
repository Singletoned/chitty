# Worker trials

How we compare work agents (harness × model × prompt) on the same tickets, what
the first round found, and how to run the next one. Scripts are in
`scripts/worker_trial/`; trial data stays in `tmp/worker-trial/` (ignored by Git).

## Why (2026-11-24 to 2026-11-25)

Workers returned sound tickets to `planning` with notes such as "no ticket
defect or external obstacle was identified". Counting outcomes in Pi's saved
sessions showed luna work sessions going from about 90% `review` and 0%
`planning` (5-14 Nov) to 33-50% `review` and 50-67% `planning` (23-24 Nov).
The person made fixing this the top priority.

Causes found:

1. **Pi 1.6.0 removed luna's reasoning.** Pi 1.6.0 (installed 2026-11-21)
   sends `reasoning.effort: "medium"` and puts the chosen level in
   `configuration_update` items for GPT-6 models (`compat.supportsMidConvoEffort`).
   For `gpt-6-luna` the Codex backend then gives almost no reasoning
   ([pi#12361](https://github.com/earendil-works/pi/issues/12361), closed but not
   released as of 2026-11-25). Share of luna calls with a thinking block: 56-70%
   (8-20 Nov), 0-15% (23-25 Nov). Broken tool calls (empty bash commands, edits
   that replace a line with itself) rose from 1-2% to 10-25%. Terra kept
   reasoning but also stalled on 1.6.0 in the trial. Fixed by downgrading the
   global Pi to 1.5.2 (`HUMAN-14` says when to move back).
2. **Provisional tickets looped.** A provisional ID was always read from the
   working tree, so the runner kept selecting a ticket its branch had returned to
   `planning`: about 70 sessions on `TASK-FER4EB` in one afternoon. Fixed by
   `TASK-664`.
3. **The work prompt grew towards leaving.** Between 10 and 24 Nov the work
   prompt grew from about 2,900 to 4,000 characters, mostly rules for returning a
   ticket; the runner's nudge also offers `planning` as an exit. The trial did
   not show this mattering once Pi was fixed (below), but the guide is being cut
   back anyway.
4. **Some tickets really were defective.** Trial workers found real defects in
   `TASK-451` (a CLI fixture missing `-d`; U+2028/U+2029 next to spaces; the
   inbox YAML round trip).

## Round 1 (2026-11-25): method

Three tickets that workers had returned, each run once per setup in its own
throwaway clone (`run_trial.sh`): `TASK-451`, `TASK-651` (no known defect) and
`TASK-664`. Setups: Pi 1.5.2 and 1.6.0 with luna and terra, Codex CLI with luna
and terra (`codex_agent.sh`), Claude Code with Haiku and Sonnet, agy with Gemini
3.8 Flash, and Pi 1.5.2 with luna and a cut-back work guide and nudge
(`lean-work.md`, variant `pi152-luna-lean`).

## Round 1: results

`review` means the worker finished and `make check` passed. Nobody has reviewed
these branches, so it is not evidence of correct work. Cost is API list price
(`costs.py`), for comparison only: the sessions ran on subscriptions.

`TASK-651` (no defects; every run started from the same ticket text):

| Setup | Outcome | Minutes | Cost (USD) |
|---|---|---|---|
| Pi 1.6.0 + luna | `planning`, on a false claim | 12 | 0.003 |
| Pi 1.6.0 + terra | `error`: stalled, nothing committed | 18 | 0.033 |
| Pi 1.5.2 + luna | `review` | 71 | 0.046 |
| Pi 1.5.2 + luna, lean prompt | `review` | 23 | 0.046 |
| Pi 1.5.2 + terra | `review` | 28 | 0.097 |
| Codex + luna | `review` | 50 | 0.088 |
| Codex + terra | `review` | 18 | 0.310 |
| Claude Code + Haiku | `review` | 50 | 0.086 |
| Claude Code + Sonnet | `review` | 50 | 0.644 |
| agy + Gemini 3.8 Flash | `review` | 58 | 4.747 |

`TASK-664` (from a base before it landed): every setup reached `review`, mostly
in 8-25 minutes; cost per setup was in the same order as above (luna on Pi or
Codex about 0.01-0.02, Haiku 0.03, terra 0.03-0.17, Sonnet 0.32, agy 0.51).

`TASK-451` (really defective): Codex + luna and terra on Pi 1.5.2 and Codex
returned it for the missing `-d`; Sonnet and terra on Pi 1.6.0 (given a version
with that fixed) found the U+2028/U+2029 and inbox defects; Pi 1.6.0 + luna gave
up without finding anything; Haiku, agy and Pi 1.5.2 + luna reached `review`
(not checked).

Conclusions: Pi 1.6.0 was the main cause; on Pi 1.5.2 both luna and terra
finish. The lean prompt was no better than the baseline once Pi was fixed. For
cost per finished ticket luna on Pi 1.5.2 was cheapest, then Codex + luna and
Haiku (same per-token price as luna, but longer sessions), then terra; Codex +
terra was fastest; agy cost the most by far.

Why agy cost so much: on `TASK-451` and `TASK-651` about 60% of its ~350 steps
(210 and 225) were `manage_task` status calls, polling a background `make check`
or pytest every few seconds, sometimes over 120 in a row. Those polls were about
70-75% of the cost, and they grew the context from about 140k to 250k tokens,
which every later step re-read. On `TASK-664` it hardly polled (4 calls) and
cost 0.51. Pi, Claude Code and Codex run commands in blocking calls, so they
cannot fall into this. Gemini 3.8 Flash is also not a cheap model here: per
token it costs 7.5 times luna or Haiku, and more than terra for cache reads.
Even without the polling it would cost about twice Sonnet. agy has no model at
luna's price; `gpt-oss-120b-medium` is the nearest, and a Gemini 4 model may
take fewer steps. Its cost figures need no cache-storage fee: implicit caching
has none.

## Pitfalls (each cost a rerun in round 1)

- **Work landing during the trial.** `TASK-664` landed on the real `main`
  mid-round, so later clones already had the fix. Always pass a fixed `base`.
- **Ticket text changing during the trial.** A ticket whose latest text is on its
  branch changes as planners and real workers edit it; one run read another run's
  findings from it. Pass a fixed `ticket-branch-start`, or use done tickets
  started from `find_base.sh`.
- **Editing a script while it runs.** `sh` reads a script as it goes; editing
  `run_trial.sh` mid-round corrupted running copies (one result row was lost).
  Copy it instead.
- **Waiting loops that match themselves.** `while pgrep -f "run_trial.sh"` also
  matches the waiting shell's own command line and never ends.
- **agy `-c`** continues the machine's most recent conversation, not the one for
  the directory; run one agy trial at a time.
- **The caller's `PATH`.** A trial started from a shell whose `PATH` holds the
  real repository's `.venv/bin` lets a bare `pytest` there import the real
  `main`'s code. At older bases the clone's own `.venv` has no `pytest`, so in
  round 2 luna ran its placeholder check against the landed code. It then
  returned `TASK-512` with a false claim that the properties pass without the
  change. `run_trial.sh` now removes every `.venv/bin` from `PATH`.
- **Relative `PYTHONPATH` in hidden tests.** A test that starts Python in a
  temporary directory loses a relative `PYTHONPATH=src` and imports the clone's
  install of the base code instead. Every `TASK-515` run first failed this way.
  `hidden_tests.sh` now uses an absolute path.
- **Stale inbox entries.** Each clone's project gets an inbox entry recording
  its path. If a later run reuses the project name after that clone is deleted,
  every `chitty` command fails with `Not a directory`. The project name now
  includes the trial folder's name.
- **agy polling.** agy runs long commands in the background and its model may
  poll them in a tight loop (see above). Count `manage_task` steps in its
  transcript before reading anything into its cost.
- **agy cost matching** needs at least 10 mentions of the clone path in a
  transcript, so it would miss a very short run; subagents, which agy did not
  start in round 1, have their own transcripts and would also be missed.
- **Codex** waits on stdin when it is not a terminal (`codex_agent.sh` closes it),
  and takes `-c` as a config override, so the wrapper maps the runner's `-c` to
  `codex exec resume --last`.
- **The lean variant** changes text a test asserts (`tests/test_run_continue.py`);
  `run_trial.sh` updates that test too, or the runner's pre-session check fails.
- Pi, Codex and Claude Code use your own global settings and hooks, as a real
  runner would.

## Round 2: plan (started 2026-11-25)

Purpose: compare setups on tickets known to be well planned and completable, and
compare the code they write. Candidates are done tickets that landed since
2026-11-19 with no return to `planning`, no failed review and no `error`, whose
implementation is one commit of 40-150 lines with tests, each in a different area:

| Ticket | Area | Reference commit | Lines (src+tests) |
|---|---|---|---|
| `TASK-512` | criterion text edits (`model.py`, `renumbering.py`) | `944d1584` | +85/-9 |
| `TASK-515` | Git metadata cache (`store.py`) | `4624ab19` | +109/-8 |
| `TASK-559` | dot-files in context directories (`ids.py`, `store.py`) | `37676040` | +92/-1 |
| `TASK-609` | landing check returns to `doing` (`run.py`) | `bc7b1c89` | +47/-9 |
| `TASK-639` | `discovered_contexts` cache (`store.py`) | `800466c4` | +53/-1 |

Other candidates found the same way: `TASK-504`, `TASK-481`, `TASK-611`,
`TASK-620`, `TASK-672`, `TASK-555`, `TASK-511`, `TASK-508`, `TASK-415`,
`TASK-407`. Each base is `main` just before a worker claimed the ticket
(`find_base.sh`), so the ticket is `todo` with the planner's final text and no
worker notes, and the runner and guides are those of that day.

Code quality, per run:

1. Outcome, minutes and cost (`results.tsv`, `costs.py`).
2. **Hidden tests**: `hidden_tests.sh` runs the reference commit's test files
   against the trial's code. A failure may only mean different names; read it.
3. Diff against the reference: size and files touched.
4. A blind review: give a reviewer agent the ticket, the trial diff and the
   reference diff unlabelled, and a fixed rubric (criteria met, test strength,
   simplicity, fit with existing code). Not scripted yet.

## Running a round

```sh
sh scripts/worker_trial/setup.sh               # Pi 1.5.2 and 1.6.0 under tmp/
export TRIAL_DIR=tmp/worker-trial/round2
sh scripts/worker_trial/run_queue.sh scripts/worker_trial/round2.queue 3
sh scripts/worker_trial/run_queue.sh scripts/worker_trial/round2-agy.queue 1
python3 scripts/worker_trial/costs.py "$TRIAL_DIR"
sh scripts/worker_trial/hidden_tests.sh pi152-luna TASK-512
```

`round2.queue` is 35 runs (5 tickets × 7 setups) and takes several hours at
parallel 3; each run's `make check` is heavy. Watch the processes, not only
`results.tsv`: a run that dies writes no row. Round 1's data is in
`tmp/worker-trial/` (`results.tsv`, `costs.tsv`, `runs/`) on the machine that
ran it.

`round2-agy.queue` uses `agy-hydrogen` (Gemini 4 Hydrogen, medium), not round
1's Gemini 3.8 Flash, which spent most of its steps polling (decided with the
person, 2026-11-25). Its price in `costs.py` ($1.50 / $7.50 / $0.075 cached)
comes from secondary sources, not Google's own page.
