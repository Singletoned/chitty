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
- `pi_check.py`: causes of large uncached inputs, and tool argument sizes.
- `pi_capture_prompt.py OUT_DIR [pi options...]`: capture the real system prompt
  and tool definitions against a local stub, without contacting a provider.

Billing totals are exact. Splits within a call are estimated from characters,
then scaled to that call's exact total. Model calls that Pi does not log, such
as observational memory's, are not counted.
