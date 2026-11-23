import ast
import asyncio
import os
import re
import subprocess
import unittest
from pathlib import Path

from click.testing import CliRunner

from chitty.cli import cli
from chitty.config import load_repo_config
from chitty.errors import ChittyError
from chitty.mcp import create_server
from chitty.store import GUIDE_BEGIN, GUIDE_END, managed_guide, repository_guide
from tests.test_cli import CliTestCase

# Keep a literal snapshot of the expected installed runner guide.
RUNNER_TEXT = (Path(__file__).parent / "fixtures/guide-runner-expected.md").read_text()

RUNNER_ONLY_SENTENCE = "When starting an agent by hand, run the matching focused guide:"
TICKETS_TEXT_END = "`plan/<name>` or `hotfix/<name>`, run the checks, then fast-forward `main`.\n"
TICKETS_TEXT = RUNNER_TEXT[: RUNNER_TEXT.index(TICKETS_TEXT_END) + len(TICKETS_TEXT_END)]
SRC = Path(__file__).resolve().parent.parent / "src" / "chitty"


def flat(text: str) -> str:
    return " ".join(text.split())


def expected_text(workflow: str) -> str:
    # Literal texts, not managed_guide(), so a broken managed_guide cannot match itself.
    return {"tickets": TICKETS_TEXT, "runner": RUNNER_TEXT}[workflow]


def managed_block(workflow: str) -> str:
    text = expected_text(workflow).rstrip("\n")
    return f"{GUIDE_BEGIN}\n\n{text}\n\n{GUIDE_END}\n"


class WorkflowCase(CliTestCase):
    def set_workflow(self, workflow: str) -> None:
        config = self.root / "chitty.toml"
        text = re.sub(r"(?m)^workflow = .*\n", "", config.read_text())
        config.write_text(
            text.replace("autocommit = false", f'workflow = "{workflow}"\nautocommit = false')
        )


class TestManagedGuide(WorkflowCase):
    def test_runner_block_matches_the_expected_guide(self):
        self.assertEqual(managed_guide("runner"), RUNNER_TEXT)

    def test_tickets_block_is_the_first_paragraph(self):
        self.assertEqual(managed_guide("tickets"), TICKETS_TEXT)

    def test_unknown_workflow_is_an_error(self):
        with self.assertRaises(ChittyError):
            managed_guide("other")

    def test_repository_guide_follows_the_config_workflow(self):
        self.set_workflow("tickets")
        self.assertEqual(repository_guide(self.root), TICKETS_TEXT)
        self.set_workflow("runner")
        self.assertEqual(repository_guide(self.root), RUNNER_TEXT)

    def test_repository_guide_outside_a_repository_is_runner(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        self.assertEqual(repository_guide(outside), RUNNER_TEXT)


class TestWorkflowBlockInstalled(WorkflowCase):
    def test_init_writes_the_tickets_block(self):
        self.set_workflow("tickets")
        self.run_cli("init")
        self.assertIn(managed_block("tickets"), (self.root / "AGENTS.md").read_text())

    def test_init_writes_the_runner_block(self):
        self.set_workflow("runner")
        self.run_cli("init")
        self.assertIn(managed_block("runner"), (self.root / "AGENTS.md").read_text())

    def test_fresh_init_writes_the_block_its_new_config_selects(self):
        self.run_cli("init")
        workflow = load_repo_config(self.root).workflow
        self.assertIn(managed_block(workflow), (self.root / "AGENTS.md").read_text())

    def test_guide_command_prints_the_repository_workflow(self):
        self.set_workflow("tickets")
        self.assertEqual(self.run_cli("guide").stdout, TICKETS_TEXT)
        self.set_workflow("runner")
        self.assertEqual(self.run_cli("guide").stdout, RUNNER_TEXT)

    def test_guide_command_outside_a_repository_is_runner(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        os.chdir(outside)
        result = CliRunner().invoke(cli, ["guide"], catch_exceptions=False)
        self.assertEqual(result.stdout, RUNNER_TEXT)

    def test_server_instructions_and_resource_follow_the_workflow(self):
        for workflow, text in (("tickets", TICKETS_TEXT), ("runner", RUNNER_TEXT)):
            with self.subTest(workflow=workflow):
                self.set_workflow(workflow)
                server = create_server(self.root)
                self.assertEqual(server.instructions, text)
                contents = list(asyncio.run(server.read_resource("chitty://guide")))
                self.assertEqual([c.content for c in contents], [text])  # type: ignore[union-attr]

    def test_server_outside_a_repository_is_runner(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        self.assertEqual(create_server(outside).instructions, RUNNER_TEXT)

    def test_import_writes_the_tickets_block(self):
        self.set_workflow("tickets")
        self.legacy_repo()
        self.run_cli("import", "backlog-md")
        agents = (self.root / "AGENTS.md").read_text()
        self.assertIn(TICKETS_TEXT.rstrip("\n"), agents)
        self.assertNotIn(RUNNER_ONLY_SENTENCE, agents)

    def test_import_writes_the_runner_block(self):
        self.set_workflow("runner")
        self.legacy_repo()
        self.run_cli("import", "backlog-md")
        agents = (self.root / "AGENTS.md").read_text()
        self.assertIn(RUNNER_TEXT.rstrip("\n"), agents)
        self.assertIn(RUNNER_ONLY_SENTENCE, agents)

    def legacy_repo(self) -> None:
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )
        (self.root / "AGENTS.md").write_text("## Backlog.md Workflow\n\nOld instructions.\n")
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "legacy backlog")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, check=True, text=True
        ).stdout


class TestWorkflowChangesReplaceOnlyTheBlock(WorkflowCase):
    def test_switching_workflow_replaces_only_the_block(self):
        agents = self.root / "AGENTS.md"
        self.set_workflow("runner")
        self.run_cli("init")
        agents.write_text(
            "# Before\n\nKeep this.\n\n" + agents.read_text() + "\n## After\n\nKeep too.\n"
        )
        self.set_workflow("tickets")
        self.run_cli("init")
        switched = agents.read_text()
        self.assertIn(managed_block("tickets"), switched)
        self.assertNotIn(managed_block("runner"), switched)
        self.assertTrue(switched.startswith("# Before\n\nKeep this.\n\n"))
        self.assertTrue(switched.endswith("\n## After\n\nKeep too.\n"))

        self.set_workflow("runner")
        self.run_cli("init")
        restored = agents.read_text()
        self.assertIn(managed_block("runner"), restored)
        self.assertNotIn(managed_block("tickets"), restored)
        self.assertTrue(restored.startswith("# Before\n\nKeep this.\n\n"))
        self.assertTrue(restored.endswith("\n## After\n\nKeep too.\n"))

    def test_damaged_markers_write_no_file(self):
        agents = self.root / "AGENTS.md"
        (self.root / "chitty.toml").unlink()
        damaged = f"{GUIDE_END}\n"
        agents.write_text(damaged)
        result = self.run_cli("init", exit_code=1)
        self.assertIn("AGENTS.md", result.stderr)
        self.assertEqual(agents.read_text(), damaged)
        self.assertFalse((self.root / "chitty.toml").exists())


class TestNoPrivateMcpNames(unittest.TestCase):
    def test_mcp_module_uses_no_underscore_names_from_the_library(self):
        tree = ast.parse((SRC / "mcp.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("mcp"):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith("_"), alias.name)
            if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
                self.assertFalse(node.attr.startswith("_"), node.attr)


class TestSplitGuide(unittest.TestCase):
    def test_no_sentence_of_the_tickets_block_is_repeated_in_runner(self):
        body = TICKETS_TEXT.split("\n", 1)[1]
        runner_file = flat((SRC / "guide-runner.md").read_text())
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat(body)) if s.strip()]
        self.assertTrue(sentences)
        for sentence in sentences:
            self.assertNotIn(sentence, runner_file)
