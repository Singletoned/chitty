# Build order

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
