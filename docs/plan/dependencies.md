# Dependencies

`depends_on` may reference any context in the same repo (`TASK-3` blocked on
`HUMAN-1` is the common case). Rules:

- A reference to an ID that doesn't exist in the repo is a `check` error.
- A reference to an archived task is fine; archived is not deleted.
- `move` gives the task a new ID in the target context and rewrites every
  reference to the old ID across the repo, reporting which files it touched.
- User-level contexts are write targets only; nothing can depend on a task
  in another repo. If you need to track it, write the foreign ID in your own
  task's Notes.
