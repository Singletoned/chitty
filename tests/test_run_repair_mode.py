from pathlib import Path

from tests.test_run_continue import TestRunContinue


class TestRunRepairMode(TestRunContinue):
    def use_mode_command(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                'agent_command = "fake-agent {mode} {id} {prompt}"',
                'agent_command = "fake-agent {mode} {id}"',
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "mode command")

    def test_error_ticket_gets_repair_mode(self):
        self.use_mode_command()
        ticket = self.json("add", "Repair ticket", "-d", "Description.", "-s", "todo")["id"]
        self.run_cli("edit", ticket, "-s", "error")
        self.write_fake("text = text.replace('status: error', 'status: review')")
        self.run_cli("run", "--errors")
        self.assertEqual(self.invocations_seen()[0], ["repair", ticket])

    def test_todo_ticket_gets_work_mode(self):
        self.use_mode_command()
        ticket = self.json("add", "Work ticket", "-d", "Description.", "-s", "todo")["id"]
        self.write_fake("text = text.replace('status: todo', 'status: review')")
        self.run_cli("run", "--ticket", ticket)
        self.assertEqual(self.invocations_seen()[0], ["work", ticket])

    def test_review_ticket_gets_review_mode(self):
        self.use_mode_command()
        ticket = self.json("add", "Review ticket", "-d", "Description.", "-s", "review")["id"]
        self.git("branch", ticket.lower())
        self.write_fake("text = text.replace('status: review', 'status: doing')")
        self.run_cli("run", "--ticket", ticket)
        self.assertEqual(self.invocations_seen()[0], ["review", ticket])

    def test_prompt_command_uses_repair_guide(self):
        ticket = self.json("add", "Repair prompt", "-d", "Description.", "-s", "todo")["id"]
        self.run_cli("edit", ticket, "-s", "error")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                'agent_command = "fake-agent {mode} {id} {prompt}"',
                'agent_command = "fake-agent {prompt}"',
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "prompt command")
        from chitty.store import guide

        fake = self.bindir / "fake-agent"
        fake.write_text(
            f"#!{__import__('sys').executable}\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            f"Path({str(self.invocations)!r}).open('a').write(repr(sys.argv[1:]) + '\\n')\n"
            "assert sys.argv[1] == "
            + repr(guide("repair", ticket, directory=Path.cwd(), workflow="runner"))
            + "\n"
            f"path = next(Path('chitty/tasks').glob('{ticket}--*.md'))\n"
            "path.write_text(path.read_text().replace('status: error', 'status: review'))\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'repair'], check=True)\n"
            "Path('repair.py').write_text('fixed = True\\n')\n"
            "subprocess.run(['git', 'add', 'repair.py'], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'repair work'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | __import__("stat").S_IXUSR)
        self.run_cli("run", "--errors")
        self.assertEqual(
            self.invocations_seen(),
            [[guide("repair", ticket, directory=Path.cwd(), workflow="runner")]],
        )
        self.assertEqual(self.json("show", ticket)["status"], "review")
