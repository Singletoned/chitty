# Dependencies

- `depends_on` may name a ticket in any context of the same repository
  (`TASK-3` waiting on `HUMAN-1` is the common case).
- An ID that does not exist is a `check` error. An archived ticket is fine.
- `move` gives the ticket a new ID and rewrites every reference to the old one,
  reporting the files it touched.
- Nothing depends on another repository's ticket. Name it in Notes instead.
