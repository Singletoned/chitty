import json
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from chitty.cli import cli


class ClaudeUsageTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.tmp = Path(self.directory.name)
        self.usage = self.tmp / "usage.json"
        self.transcript = self.tmp / "session.jsonl"

    def invoke(self, request: dict[str, str], *, usage: Path | None = None):
        environment = {} if usage is None else {"CHITTY_USAGE_FILE": str(usage)}
        return CliRunner().invoke(
            cli,
            ["claude-usage-hook"],
            input=json.dumps(request),
            env=environment,
            catch_exceptions=False,
        )

    def write_transcript(self, path: Path, entries: list[object]) -> None:
        path.write_text("".join(json.dumps(entry) + "\n" for entry in entries))

    def test_sums_unique_messages_in_transcript_and_subagent(self):
        self.write_transcript(
            self.transcript,
            [
                {"message": {"role": "user"}},
                {
                    "message": {
                        "id": "message-1",
                        "role": "assistant",
                        "model": "claude-sonnet",
                        "usage": {"input_tokens": 10, "output_tokens": 2},
                    }
                },
                {
                    "message": {
                        "id": "message-1",
                        "role": "assistant",
                        "model": "claude-sonnet",
                        "usage": {"input_tokens": 10, "output_tokens": 2},
                    }
                },
            ],
        )
        subagents = self.transcript.with_suffix("") / "subagents"
        subagents.mkdir(parents=True)
        self.write_transcript(
            subagents / "agent-abc.jsonl",
            [
                {
                    "message": {
                        "id": "message-2",
                        "role": "assistant",
                        "model": "claude-haiku",
                        "usage": {
                            "input_tokens": 3,
                            "output_tokens": 4,
                            "cache_read_input_tokens": 5,
                            "cache_creation_input_tokens": 6,
                        },
                    }
                }
            ],
        )

        result = self.invoke(
            {"session_id": "session-1", "transcript_path": str(self.transcript)},
            usage=self.usage,
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            json.loads(self.usage.read_text()),
            {
                "sessions": {
                    "session-1": [
                        {
                            "provider": "anthropic",
                            "model": "claude-sonnet",
                            "input": 10,
                            "output": 2,
                            "cacheRead": 0,
                            "cacheWrite": 0,
                            "cost": None,
                        },
                        {
                            "provider": "anthropic",
                            "model": "claude-haiku",
                            "input": 3,
                            "output": 4,
                            "cacheRead": 5,
                            "cacheWrite": 6,
                            "cost": None,
                        },
                    ]
                }
            },
        )

    def test_errors_are_reported_without_failing_the_hook(self):
        cases = (
            (
                {"session_id": "session-1", "transcript_path": str(self.tmp / "missing")},
                "No such file",
            ),
            (
                {"session_id": "session-1", "transcript_path": str(self.transcript)},
                "Expecting value",
            ),
            ({"transcript_path": str(self.transcript)}, "session_id"),
        )
        self.transcript.write_text("not json\n")
        for request, message in cases:
            with self.subTest(message=message):
                result = self.invoke(request, usage=self.usage)
                self.assertEqual(result.exit_code, 0)
                self.assertIn(message, result.stderr)
        self.transcript.write_text("{}\n")
        self.usage.write_text("[]")
        result = self.invoke(
            {"session_id": "session-1", "transcript_path": str(self.transcript)},
            usage=self.usage,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("sessions", result.stderr)
        self.assertEqual(self.usage.read_text(), "[]")

    def test_unset_file_does_nothing_and_valid_file_keeps_other_sessions(self):
        self.transcript.write_text("")
        result = self.invoke({"session_id": "session-1", "transcript_path": "missing"})
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(self.usage.exists())

        self.usage.write_text(json.dumps({"sessions": {"other": []}}))
        result = self.invoke(
            {"session_id": "session-1", "transcript_path": str(self.transcript)},
            usage=self.usage,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            json.loads(self.usage.read_text())["sessions"], {"other": [], "session-1": []}
        )
