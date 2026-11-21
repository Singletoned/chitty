from tests.test_run_continue import TestRunContinue


class TestRepairRequiresWork(TestRunContinue):
    def test_repair_requires_committed_work_outside_ticket_directories(self):
        cases = ("edit", "uncommitted", "code", "blocked")
        for case_name in cases:
            with self.subTest(case=case_name):
                case = type(self)(self._testMethodName)
                case.setUp()
                try:
                    case._run_repair_case(case_name)
                finally:
                    case.doCleanups()

    def _run_repair_case(self, case_name):
        ticket = self.json("add", "Broken", "-d", "Description.", "-s", "error")["id"]
        self.git("branch", ticket.lower())
        script = (
            "from pathlib import Path\n"
            "import subprocess\n"
            f"ticket = next(Path('chitty/tasks').glob('{ticket}--*.md'))\n"
        )
        if case_name == "edit":
            script += (
                f"subprocess.run(['chitty', 'edit', {ticket!r}, '-s', 'review'], check=True)\n"
            )
        elif case_name == "code":
            script += (
                "Path('repair.py').write_text('fixed = True\\n')\n"
                "subprocess.run(['git', 'add', 'repair.py'], check=True)\n"
                "subprocess.run(['git', 'commit', '--quiet', '-m', 'Repair', "
                f"'-m', 'Task: {ticket}'], "
                "check=True)\n"
                f"subprocess.run(['chitty', 'edit', {ticket!r}, '-s', 'review'], check=True)\n"
            )
        elif case_name == "uncommitted":
            script += (
                "ticket.write_text(ticket.read_text().replace('status: error', 'status: review'))\n"
            )
        else:
            script += (
                "ticket.write_text(ticket.read_text().replace("
                "'status: error', 'status: blocked'))\n"
                "subprocess.run(['git', 'add', str(ticket)], check=True)\n"
                "subprocess.run(['git', 'commit', '--quiet', '-m', 'blocked'], check=True)\n"
            )
        fake = self.bindir / "fake-agent"
        fake.write_text(f"#!{__import__('sys').executable}\n" + script)
        fake.chmod(fake.stat().st_mode | __import__("stat").S_IXUSR)
        if case_name == "uncommitted":
            result = self.run_cli("run", "--errors", exit_code=1)
            self.assertIn(
                f"repair agent left {ticket} in invalid status error; expected review or blocked",
                result.stderr,
            )
            ticket_file = next((self.root / "chitty" / "tasks").glob(f"{ticket}--*.md"))
            self.assertIn("\nstatus: error\n", ticket_file.read_text())
        elif case_name == "edit":
            result = self.run_cli("run", "--errors", exit_code=1)
            self.assertIn(
                f"repair agent returned {ticket} to review with no change beyond its ticket files",
                result.stderr,
            )
            # `chitty show` prefers the repair branch's newer committed version,
            # so read the main checkout's own ticket file.
            ticket_file = next((self.root / "chitty" / "tasks").glob(f"{ticket}--*.md"))
            self.assertIn("\nstatus: error\n", ticket_file.read_text())
        else:
            result = self.run_cli("run", "--errors")
            expected = "blocked" if case_name == "blocked" else "review"
            self.assertEqual(self.json("show", ticket)["status"], expected, result.stderr)
