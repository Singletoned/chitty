"""Resolve a stable, human-readable actor name from coding-agent environments."""

import hashlib
import os
from collections.abc import Mapping

from chitty.errors import ChittyError

_ADJECTIVES = (
    "able",
    "brisk",
    "calm",
    "daring",
    "eager",
    "friendly",
    "golden",
    "honest",
    "intrepid",
    "jolly",
    "kind",
    "lively",
    "mellow",
    "nimble",
    "open",
    "plucky",
    "quick",
    "rosy",
    "sunny",
    "tidy",
    "upbeat",
    "vivid",
    "witty",
    "youthful",
    "zesty",
)
_ANIMALS = (
    "adder",
    "badger",
    "crane",
    "dormouse",
    "eel",
    "falcon",
    "gannet",
    "heron",
    "ibis",
    "jay",
    "kestrel",
    "lapwing",
    "marten",
    "newt",
    "otter",
    "puffin",
    "quail",
    "raven",
    "stoat",
    "toad",
    "urchin",
    "vole",
    "wren",
    "yellowhammer",
    "zander",
)

_COLOURS = (
    "amber",
    "bronze",
    "coral",
    "dusky",
    "ebony",
    "fawn",
    "ginger",
    "hazel",
    "indigo",
    "jade",
    "khaki",
    "lilac",
    "maroon",
    "navy",
    "ochre",
    "pearl",
    "quartz",
    "russet",
    "silver",
    "teal",
    "umber",
    "violet",
    "white",
    "yellow",
    "zinc",
)
_SESSION_IDENTITIES = (
    ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"),
    ("CHITTY_PI_SESSION_ID", "PI_SESSION_ID"),
    ("PI_SESSION_ID", "PI_SESSION_ID"),
    ("CODEX_THREAD_ID", "CODEX_THREAD_ID"),
    ("CODEX_SESSION_ID", "CODEX_SESSION_ID"),
    ("ANTIGRAVITY_CONVERSATION_ID", "ANTIGRAVITY_CONVERSATION_ID"),
)


def run_actor(identity: str) -> str:
    """Return the readable actor name for a `chitty run` session."""
    return _readable_name("CHITTY_RUN", identity)


def actor(environment: Mapping[str, str] | None = None) -> str:
    """Return the explicit or harness-derived name for this actor."""
    env = os.environ if environment is None else environment
    if override := env.get("CHITTY_ACTOR", "").strip():
        return override
    for variable, source in _SESSION_IDENTITIES:
        if identity := env.get(variable, "").strip():
            return _readable_name(source, identity)
    names = ", ".join(variable for variable, _ in _SESSION_IDENTITIES)
    raise ChittyError(f"cannot determine actor; set CHITTY_ACTOR or provide one of {names}")


def _readable_name(source: str, identity: str) -> str:
    digest = hashlib.sha256(f"{source}:{identity}".encode()).digest()
    adjective = _ADJECTIVES[digest[0] % len(_ADJECTIVES)]
    colour = _COLOURS[digest[1] % len(_COLOURS)]
    animal = _ANIMALS[digest[2] % len(_ANIMALS)]
    return f"{adjective}-{colour}-{animal}"


def pi_session_environment_missing(environment: Mapping[str, str] | None = None) -> bool:
    """Whether a Pi agent lacks the identity its shell session should expose.

    `CHITTY_ACTOR` supplies one, as `chitty run` does for print-mode Pi.
    """
    env = os.environ if environment is None else environment
    return (
        env.get("PI_CODING_AGENT") == "true"
        and not any(env.get(variable, "").strip() for variable, _ in _SESSION_IDENTITIES)
        and not env.get("CHITTY_ACTOR", "").strip()
    )
