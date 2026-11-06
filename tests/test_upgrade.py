import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from chitty import upgrade
from chitty.cli import main


class _PyPIHandler(BaseHTTPRequestHandler):
    requests = 0
    version = "0.1.31"

    def do_GET(self):
        type(self).requests += 1
        body = json.dumps({"info": {"version": self.version}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


class UpgradeTest(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.TemporaryDirectory()
        self.addCleanup(self.data.cleanup)
        self.pending = Path(self.data.name) / "chitty" / "pending-release"
        self.count = self.pending.parent / "upgrade-count"
        self.pending.parent.mkdir(parents=True)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _PyPIHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.addCleanup(self.thread.join)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        _PyPIHandler.requests = 0
        self.patchers = [
            mock.patch.dict(os.environ, {"XDG_DATA_HOME": self.data.name}, clear=False),
            mock.patch.object(upgrade, "_is_editable_install", return_value=False),
            mock.patch.object(
                upgrade,
                "PYPI_URL",
                f"http://{self.server.server_address[0]}:{self.server.server_address[1]}",
            ),
            mock.patch.object(upgrade, "UPGRADE_RETRY_SECONDS", 0),
            mock.patch.object(upgrade, "__version__", "0.1.30"),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_main_alerts_after_release_and_preserves_exit(self):
        self.pending.write_text("0.1.31\n")
        os.utime(self.pending, (0, 0))
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            _PyPIHandler.version = "0.1.30"
            upgrade.check_for_upgrade()
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(_PyPIHandler.requests, 1)

        _PyPIHandler.version = "0.1.31"
        with (
            mock.patch("chitty.cli.cli", side_effect=SystemExit(7)),
            self.assertRaises(SystemExit) as raised,
            contextlib.redirect_stderr(output),
        ):
            main()
        self.assertEqual(raised.exception.code, 7)
        self.assertEqual(_PyPIHandler.requests, 2)
        self.assertEqual(self.pending.read_text(), "0.1.31\nout\n")
        self.assertIn("chitty 0.1.31 is out", output.getvalue())

        with mock.patch.object(upgrade, "__version__", "0.1.31"):
            upgrade.check_for_upgrade()
        self.assertFalse(self.pending.exists())
        self.assertEqual(_PyPIHandler.requests, 2)

    def test_recent_failure_is_not_retried(self):
        self.pending.write_text("0.1.31\n")
        with mock.patch.object(upgrade.urllib.request, "urlopen", side_effect=OSError):
            upgrade.check_for_upgrade()
            upgrade.check_for_upgrade()
        self.assertEqual(self.pending.read_text(), "0.1.31\n")

    def test_unreadable_file_is_ignored(self):
        self.pending.write_text("0.1.31\n")
        original_read_text = Path.read_text

        def unreadable(path: Path) -> str:
            if path == self.pending:
                raise OSError("unreadable")
            return original_read_text(path)

        with mock.patch.object(Path, "read_text", unreadable):
            upgrade.check_for_upgrade()
        self.assertTrue(self.pending.exists())
        self.assertEqual(_PyPIHandler.requests, 0)

    def test_checks_pypi_on_100th_command(self):
        for _ in range(99):
            upgrade.check_for_upgrade()
        self.assertEqual(_PyPIHandler.requests, 0)
        self.assertEqual(self.count.read_text(), "99")

        upgrade.check_for_upgrade()

        self.assertEqual(_PyPIHandler.requests, 1)
        self.assertEqual(self.count.read_text(), "0")
        self.assertEqual(self.pending.read_text(), "0.1.31\nout\n")

    def test_failed_pypi_check_leaves_reset_count(self):
        self.count.write_text("99")
        with mock.patch.object(upgrade.urllib.request, "urlopen", side_effect=OSError):
            upgrade.check_for_upgrade()
        self.assertEqual(self.count.read_text(), "0")
        self.assertFalse(self.pending.exists())

    def test_editable_install_is_silent(self):
        self.pending.write_text("0.1.31\n")
        with mock.patch.object(upgrade, "_is_editable_install", return_value=True):
            upgrade.check_for_upgrade()
        self.assertTrue(self.pending.exists())
        self.assertFalse(self.count.exists())


if __name__ == "__main__":
    unittest.main()
