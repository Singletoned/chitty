# Pi token analysis

Read-only analysis of Pi's saved sessions, with no LLM involved. Pass one or
more session directories. For this project:

```sh
python3 scripts/pi_tokens.py ~/.pi/agent/sessions/*chitty*
```

- `pi_tokens.py`: spend by model, billing kind, and what was in context.
- `pi_coldstart.py`: first-call size and cost before the first edit.
- `pi_usage.py`: tools and skills used, and which files are carried longest.
- `pi_commands.py`: every command agents ran, split out of compound shell.
- `pi_reads.py`: how much of each file is read, and whether reads seemed to matter.
- `pi_calls.py`: what model calls were for, by purpose, context size and phase.
- `pi_check.py`: causes of large uncached inputs, and tool argument sizes.
- `pi_capture_prompt.py OUT_DIR [pi options...]`: capture the real system prompt
  and tool definitions against a local stub, without contacting a provider.

Billing totals are exact. Splits within a call are estimated from characters,
then scaled to that call's exact total. Model calls that Pi does not log, such
as observational memory's, are not counted.

# Retro numbers

`python3 scripts/retro.py REPO [REPO ...]` prints, per ISO week, reviews passed
and failed, first-review pass rates with and without a cold read, `chitty run`
sessions and hours, and the share of Chitty autocommits; then failure causes
and the tickets that failed review most often. It reads ticket files, `git log`
and the machine-local usage log, and changes nothing.

# Worker trials

`scripts/worker_trial/` runs one `chitty run` work session per ticket and setup
(harness, model, prompt) in throwaway clones, then compares outcome, time,
API-equivalent cost and code against the landed reference. Method, round 1
results and the round 2 plan: `docs/plan/worker-trials.md`.
