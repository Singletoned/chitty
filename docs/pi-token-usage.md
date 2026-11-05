# Reducing Pi token costs on Chitty

Tickets: `TASK-170`–`TASK-176`.

Analysis from 2026-11-04, covering 95 Chitty sessions from 2026-10-25 to
2026-11-04: 4,077 model calls and $71.68, all on `gpt-5.6-terra`. The analysis
used no AI. To reproduce it, see [`scripts/README.md`](../scripts/README.md).

**The cheapest model that can still do the work is by far the biggest saving: up
to 66–90%, if quality holds.** Everything else found here adds up to perhaps
25–35%. Most of that comes from sending less context on each call and making
fewer calls, not from smaller files.

## Where the money goes

Every call re-sends the whole context, so a call averages $0.018 however small
its command is.

| What the call was for        |   Cost | Share | Calls |
| ---------------------------- | ------ | ----- | ----- |
| Editing files                | $18.61 |   26% |   909 |
| Reading and searching        | $16.99 |   24% | 1,039 |
| `chitty` commands            | $16.25 |   23% |   862 |
| Tests, lint and formatting   | $10.92 |   15% |   656 |
| `git`                        |  $4.48 |    6% |   289 |
| Replies, subagents and other |  $4.42 |    6% |   323 |

These are exact billed costs, though sorting shell calls into categories is a
heuristic. Looked at another way:

- **By price type:** about 60% of spend is re-sending cached context, 25% is new
  input and 15% is output.
- **By session:** 7 sessions of 100+ calls take 37% of spend, while the median
  session costs $0.35.

## Recommendations

| #   | Change                                | Estimated saving             | Risk                |
| --- | ------------------------------------- | ---------------------------- | ------------------- |
| 1   | Trial cheaper models                  | 66–90% if quality holds      | Quality and rework  |
| 2   | Keep sessions shorter                 | Up to 10%                    | Low to medium       |
| 3   | Fewer workflow calls                  | About 10%                    | Low                 |
| 4   | Trim the prompt for ephemeral runs    | About 8%                     | Low                 |
| 5   | Batch read-only calls                 | 3–6%                         | Low                 |
| 6   | Narrow `PLAN.md` reads                | 3–4%                         | Low                 |
| 7   | Test whether `context-mode` pays off  | Unknown, could go either way | Needs an experiment |

The savings overlap, so they should not be added together. Only 1 and 4 come from
direct calculation; the rest are judgement based on the measurements.

### 1. Trial cheaper models

Pi's catalog prices, per million tokens:

| Model                     | Input | Output | Cached | Same tokens would cost |
| ------------------------- | ----- | ------ | ------ | ---------------------- |
| `gpt-5.6-terra` (current) | $2.00 | $12.00 |  $0.20 |                   100% |
| `gpt-6.1-terra`           | $1.00 |  $5.00 |  $0.05 |              About 34% |
| `gpt-5.6-luna`            | $0.20 |  $1.20 |  $0.02 |                    10% |

Price alone does not settle it, because a weaker model could take more calls or
fail review more often. Run the same small tickets on each model and compare
**cost per ticket that passes review**. `gpt-6.1-terra` is the obvious first try,
since it is cheaper and appears to be newer.

### 2. Keep sessions shorter

A call costs about $0.021 at 60–100k tokens of context, against $0.016 at
30–60k, and 42% of spend happens in that upper band. If all of those calls were
at the lower price, it would save about $7 (10%).

Smaller tickets are the natural way to get there, or ending the session sooner.
Earlier compaction might also help, but summaries have costs the logs do not
show, and re-reading could cancel the saving. Why the 7 longest sessions ran so
long has not been investigated, and that is worth doing first.

### 3. Fewer workflow calls

`chitty` and `git` together are 29% of spend, and most of those calls make no
direct progress on the task. A one-line `chitty edit` costs as much as any other
call, because the cost is the context rather than the command.

- **Combine ticket updates:** tick criteria and add notes in one command at each
  stage, not one per step.
- **Automate the routine git steps:** let `autocommit` or `chitty` handle what
  agents now do by hand, like checking `git status` and staging.
- **Combine check and format:** run `make format && make check` as one step.

Removing a third of these calls would save about 10%.

### 4. Trim the prompt for ephemeral runs

A session sends about 15,400 tokens before it reads the task, which is 21% of
spend. What makes up that prompt, by share of characters:

| Source                                                      | Share |
| ----------------------------------------------------------- | ----- |
| `context-mode` tools and skill listings                     |   44% |
| `subagent` tool and its instructions                        |   11% |
| Pi's own tools and instructions                             |   10% |
| Other skill listings (`cmux-*`, `rust-skills`, etc.)        |   10% |
| Global `AGENTS.md` and learned rules                        |    8% |
| This repo's `AGENTS.md` (the Chitty guide is 5 of the 7)    |    7% |
| Other extension tools                                       |    5% |

Pi's existing flags cut the prompt by 39% in a test, by removing 12 tools that
were used at most once and every skill except `python-dev`:

```sh
pi --no-skills --skill ~/.pi/agent/skills/python-dev \
  --exclude-tools 'ctx_fetch_and_index,ctx_index,ctx_purge,ctx_upgrade,ctx_insight,ctx_stats,ctx_doctor,get_development_port,recall,save_learning,brave_search,question'
```

`chitty run` could pass these flags through runner config, leaving interactive Pi
untouched. Chitty's own guide is only about 5% of the prompt, so trimming it will
not achieve much.

### 5. Batch read-only calls

Agents average only 1.11 tools per call. In 538 cases, a call with one read-only
tool came straight after another, which is about $9.50 of calls. Some of those
depend on the previous result, so expect to save a third to two-thirds of that
with a guide line asking agents to group their reads. How well the model follows
that kind of instruction has not been checked.

### 6. Narrow `PLAN.md` reads

It is the most expensive file to read, at about $3, and agents read it because
`AGENTS.md` tells them to. Point them to the relevant section or split the file
by topic. This is cheap to do and has no real downside.

### 7. Test whether `context-mode` pays off

It is 44% of the prompt, and its tool results cost another 16% of spend, but it
may be replacing bigger outputs. The logs cannot show the net effect, so the only
way to find out is to run comparable tickets with and without it.

## What not to do

- **Split code files to save tokens:** agents already read parts of large files,
  and spend levels off at about 3,300 tokens per file. Splitting could backfire,
  because small files tend to get read in full.
- **Chase "wrong file" reads:** at most about 3% of spend, with no repeat
  offender.
- **Work on cross-session caching:** about 3% at most, and it needs a change in
  Pi.
- **Trim command output:** `make check` averages about 320 tokens, so the call
  matters far more than its output.
- **Lower thinking effort for now:** reasoning is 39% of output tokens, or about
  6% of spend, and cutting it could add calls. Include it in the model trial
  instead.

## How far to trust this

- **Prices:** these are list prices. On a subscription, what matters is how each
  model counts against its limits, which has not been checked. The catalog prices
  are also not yet confirmed for the `openai-codex` account.
- **Missing costs:** calls made by the observational memory package and for
  compaction summaries are not logged, so true spend is higher.
- **Sample:** this is 95 sessions from about 10 days of one repo, and it mixes
  work and review sessions.
- **Sample drift:** sessions kept arriving during the analysis. Some sub-figures,
  such as the 21% prompt share, come from an earlier cut of 88 sessions.
- **Estimates:** billing totals are exact, but splits within a call are estimated
  from character counts, then scaled to that call's total.
- **Not tested:** none of these changes has been run yet, so the savings are
  projections.

## Suggested order

Do 4 and 6 first, because they are cheap and low-risk. Then run the model trial,
since its result decides how much the rest matters. Measure 3 and 5 by re-running
the scripts afterwards.

## Related: a bug found along the way

The Chitty guide tells agents to put code in backticks in notes. Inside a
double-quoted shell argument, the shell tries to run that text as a command. The
logs show `command not found` errors for words like `chitty_version`,
`Repo.finalize` and `todo`, and about 16 `bash` calls match the pattern. Ticket
notes have probably lost text this way, though the tickets themselves have not
been checked. Fixing it will not save money, but it affects every client.
