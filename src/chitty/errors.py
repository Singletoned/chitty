class ChittyError(Exception):
    """A user-facing error: the message says what is wrong and where."""


# An idle queue gets its own status so a loop can wait it out while still
# stopping on real failures: Click uses 1 and 2, and `chitty run` 130.
NO_NEXT_TICKET_EXIT = 3


class NoNextTicket(ChittyError):
    """Nothing is left to select: an idle queue, not a failure."""


class ManagedGuideError(ChittyError):
    """`AGENTS.md` has damaged Chitty management markers."""
