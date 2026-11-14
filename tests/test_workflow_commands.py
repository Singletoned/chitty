"""Workflow-specific CLI and MCP command availability."""

import asyncio
import os
import re
from pathlib import Path

from click.testing import CliRunner

from chitty.cli import cli
from chitty.mcp import create_server
from tests.support import CONFIG
from tests.test_cli import CliTestCase


def config_with(workflow: str) -> str:
    return CONFIG.replace(
        'default_context = "tasks"\n',
        f'default_context = "tasks"\nworkflow = "{workflow}"\n',
    )


def listed_commands(help_text: str) -> set[str]:
    return set(re.findall(r"^  (\S+)", help_text, re.MULTILINE))


def tool_names(start: Path) -> set[str]:
    return {tool.name for tool in asyncio.run(create_server(start).list_tools())}


class TestWorkflowCommands(CliTestCase):
    def write_config(self, workflow: str) -> None:
        (self.root / "chitty.toml").write_text(config_with(workflow))

    def test_tickets_help_hides_run_and_next(self):
        self.write_config("tickets")
        commands = listed_commands(self.run_cli("--help").output)
        self.assertNotIn("run", commands)
        self.assertNotIn("next", commands)
        self.assertIn("list", commands)
        self.assertIn("add", commands)

    def test_tickets_commands_refuse(self):
        self.write_config("tickets")
        for command in ("run", "next"):
            with self.subTest(command=command):
                result = CliRunner().invoke(cli, [command])
                self.assertEqual(result.exit_code, 1, result.output)
                self.assertIn(
                    f'chitty {command} needs workflow = "runner" in the Chitty config',
                    result.stderr,
                )

    def test_runner_help_lists_runner_commands(self):
        self.write_config("runner")
        commands = listed_commands(self.run_cli("--help").output)
        self.assertIn("run", commands)
        self.assertIn("next", commands)

    def test_missing_config_keeps_commands_visible(self):
        (self.root / "chitty.toml").unlink()
        outside = self.tmp / "outside"
        outside.mkdir()
        os.chdir(outside)
        commands = listed_commands(self.run_cli("--help").output)
        self.assertIn("run", commands)
        self.assertIn("next", commands)

    def test_broken_config_keeps_help_available_and_reports_error(self):
        (self.root / "chitty.toml").write_text("this is = not [valid toml\\n")
        commands = listed_commands(self.run_cli("--help").output)
        self.assertIn("run", commands)
        self.assertIn("next", commands)
        result = CliRunner().invoke(cli, ["next"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("invalid TOML", result.output)

    def test_mcp_next_follows_workflow(self):
        self.write_config("tickets")
        self.assertNotIn("next", tool_names(self.root))
        self.write_config("runner")
        self.assertIn("next", tool_names(self.root))

    def test_mcp_outside_repository_lists_next(self):
        (self.root / "chitty.toml").unlink()
        self.assertIn("next", tool_names(self.root))
