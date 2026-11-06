"""Claude Code session usage hook."""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, TextIO, cast

_TOKEN_FIELDS = {
    "input_tokens": "input",
    "output_tokens": "output",
    "cache_read_input_tokens": "cacheRead",
    "cache_creation_input_tokens": "cacheWrite",
}


def run_hook(stdin: TextIO) -> None:
    """Record one Claude session, reporting errors without failing the hook."""
    usage_file = os.environ.get("CHITTY_USAGE_FILE")
    if usage_file is None:
        return
    try:
        request = _read_json(stdin)
        session_id = request.get("session_id")
        transcript_path = request.get("transcript_path")
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("stdin is missing `session_id`")
        if not isinstance(transcript_path, str) or not transcript_path:
            raise ValueError("stdin is missing `transcript_path`")
        models = _sum_transcripts(Path(transcript_path))
        _write_usage(Path(usage_file), session_id, models)
    except Exception as error:  # noqa: BLE001 - hooks must not fail the session
        print(f"warning: cannot write Claude session usage: {error}", file=sys.stderr)


def _read_json(stream: TextIO) -> dict[str, Any]:
    value: Any = json.load(stream)
    if not isinstance(value, dict):
        raise TypeError("stdin must contain a JSON object")
    return cast(dict[str, Any], value)


def _transcript_paths(path: Path) -> list[Path]:
    paths = [path]
    subagents = path.with_suffix("") / "subagents"
    if subagents.exists():
        paths.extend(sorted(subagents.glob("agent-*.jsonl")))
    return paths


def _sum_transcripts(path: Path) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, Any]] = {}
    seen_ids: set[str] = set()
    for transcript in _transcript_paths(path):
        with transcript.open() as stream:
            for line_number, line in enumerate(stream, 1):
                entry: Any = json.loads(line)
                if not isinstance(entry, dict):
                    continue
                typed_entry = cast(dict[str, Any], entry)
                message = typed_entry.get("message")
                if not isinstance(message, dict):
                    continue
                message = cast(dict[str, Any], message)
                if message.get("role") != "assistant":
                    continue
                message_id = message.get("id")
                model = message.get("model")
                if not isinstance(message_id, str) or not message_id:
                    raise ValueError(f"{transcript}:{line_number} assistant message has no `id`")
                if not isinstance(model, str) or not model:
                    raise ValueError(f"{transcript}:{line_number} assistant message has no `model`")
                if message_id in seen_ids:
                    continue
                seen_ids.add(message_id)
                total = totals.setdefault(
                    model,
                    {
                        "provider": "anthropic",
                        "model": model,
                        "input": 0,
                        "output": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "cost": None,
                    },
                )
                raw_usage: Any = message.get("usage")
                if raw_usage is None:
                    raw_usage = {}
                if not isinstance(raw_usage, dict):
                    raise TypeError(f"{transcript}:{line_number} usage is not an object")
                usage = cast(dict[str, Any], raw_usage)
                for source, target in _TOKEN_FIELDS.items():
                    value = usage.get(source)
                    if value is not None:
                        if not isinstance(value, (int, float)) or isinstance(value, bool):
                            raise ValueError(
                                f"{transcript}:{line_number} `{source}` is not numeric"
                            )
                        total[target] += value
    return list(totals.values())


def _write_usage(path: Path, session_id: str, models: list[dict[str, Any]]) -> None:
    existing: dict[str, Any] = {"sessions": {}}
    if path.exists():
        with path.open() as stream:
            raw_existing: Any = json.load(stream)
        if not isinstance(raw_existing, dict):
            raise ValueError("usage file does not contain a `sessions` object")
        typed_existing = cast(dict[str, Any], raw_existing)
        if not isinstance(typed_existing.get("sessions"), dict):
            raise ValueError("usage file does not contain a `sessions` object")
        existing = typed_existing
    path.parent.mkdir(parents=True, exist_ok=True)
    sessions = cast(dict[str, Any], existing["sessions"])
    sessions[session_id] = models
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as stream:
            temporary = stream.name
            json.dump(existing, stream, separators=(",", ":"))
        os.replace(temporary, path)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
