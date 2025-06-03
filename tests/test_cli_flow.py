"""Tests for the Journal API CLI flow."""
import os
import subprocess
import unittest
import re
import time
from client.config import TOKEN_FILE
from app import create_app
from extensions import db

class TestJournalCLIFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a clean test environment."""
        app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        with app.app_context():
            db.create_all()

    def run_cli(self, command):
        """Run a CLI command and return stdout and stderr as strings."""
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=dict(os.environ, PYTHONPATH="."),
            text=True
        )
        return result.stdout, result.stderr

    def test_cli_end_to_end(self):
        """Test the full CLI workflow: register, login, create entry, comment, and list."""
        email = f"foo_{int(time.time())}@example.com"

        # 1. Register a new user
        out, err = self.run_cli(
            f'python client/main.py auth register --username foo --email {email} --password testpass123'
        )
        self.assertTrue("success" in out.lower() or "✅" in out or "registered" in out,
                        f"Registration failed: stdout: {out}, stderr: {err}")

        # 2. Login
        out, err = self.run_cli(
            f'python client/main.py auth login --email {email} --password testpass123'
        )
        self.assertTrue("logged in" in out.lower() or "✅" in out,
                        f"Login failed: stdout: {out}, stderr: {err}")
        self.assertTrue(os.path.exists(TOKEN_FILE), "Token file not found after login.")

        # 3. Create a journal entry
        out, err = self.run_cli(
            'python client/main.py entry create "First Post" "This is my first journal." --tags "test,cli"'
        )
        self.assertTrue("success" in out.lower() or "✅" in out,
                        f"Entry creation failed: stdout: {out}, stderr: {err}")

        # 4. List entries and extract entry ID
        out, err = self.run_cli("python client/main.py entry list")
        self.assertIn("First Post", out, f"Entry list output did not include entry title: {out}")
        lines = out.strip().splitlines()
        entry_line = next((line for line in lines if "First Post" in line), None)
        self.assertIsNotNone(entry_line, "No entry line found in output.")
        match = re.search(r"\[(\d+)\]", entry_line)
        self.assertIsNotNone(match, "Could not extract entry ID from line: " + entry_line)
        entry_id = match.group(1)

        # 5. Add a comment to the entry
        out, err = self.run_cli(f'python client/main.py comment add {entry_id} "hello!"')
        self.assertTrue("success" in out.lower() or "✅" in out,
                        f"Comment add failed: stdout: {out}, stderr: {err}")

        # 6. List comments and verify the comment exists
        out, err = self.run_cli(f"python client/main.py comment list {entry_id}")
        print("DEBUG: comment list stdout →", repr(out))
        print("DEBUG: comment list stderr →", repr(err))
        self.assertIn("hello!", out, f"Comment 'hello!' not found in output: {out}")

    @classmethod
    def tearDownClass(cls):
        """Clean up token file after tests."""
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        with app.app_context():
            db.drop_all()

if __name__ == "__main__":
    unittest.main()