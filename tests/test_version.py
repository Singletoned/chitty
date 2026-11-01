import unittest


class TestVersion(unittest.TestCase):
    def test_runtime_version_comes_from_the_source_package(self):
        from chitty import __version__
        from chitty.config import CHITTY_VERSION

        self.assertEqual(CHITTY_VERSION, __version__)
