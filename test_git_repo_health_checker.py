import os, sys, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from main import health


def make_repo(dirty=False):
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", tmp], check=True)
    subprocess.run(["git", "-C", tmp, "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", tmp, "config", "user.name", "Tester"], check=True)
    open(os.path.join(tmp, "a.txt"), "w").write("hello")
    subprocess.run(["git", "-C", tmp, "add", "."], check=True)
    subprocess.run(["git", "-C", tmp, "commit", "-qm", "init"], check=True)
    if dirty:
        open(os.path.join(tmp, "a.txt"), "a").write("more")
    return tmp


class TestRepoHealth(unittest.TestCase):
    def test_clean_repo_healthy(self):
        result = health(make_repo())
        self.assertEqual(result["verdict"], "HEALTHY")
        self.assertEqual(result["score"], 100)

    def test_dirty_repo_flagged(self):
        result = health(make_repo(dirty=True))
        self.assertLess(result["score"], 100)
        self.assertTrue(any("uncommitted" in d for d in result["details"]))

    def test_non_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(health(tmp)["verdict"], "NOT A REPO")
