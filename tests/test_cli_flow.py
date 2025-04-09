# tests/test_cli_flow.py

import os
import subprocess
import unittest
import json
from client.config import TOKEN_FILE

class TestJournalCLIFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure DB is reset for a clean test
        subprocess.run(["python", "init_db.py"], check=True)

    def run_cli(self, command):
        """Run a CLI command and return output (stdout)."""
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=dict(os.environ, PYTHONPATH="."),
        )
        return result.stdout.decode(), result.stderr.decode()

    def test_cli_end_to_end(self):
        # 1. Register
        out, err = self.run_cli(
            'python client/main.py auth register --username foo --email foo@example.com --password testpass123'
        )
        self.assertIn("✅", out or err)

        # 2. Login
        out, err = self.run_cli(
            'python client/main.py auth login --email foo@example.com --password testpass123'
        )
        self.assertIn("✅ Logged in", out or err)
        self.assertTrue(os.path.exists(TOKEN_FILE))

        # 3. Create Entry
        out, err = self.run_cli(
            'python client/main.py entry create "First Post" "This is my first journal." --tags "test,cli"'
        )
        self.assertIn("✅", out or err)

        # 4. List Entries
        out, err = self.run_cli("python client/main.py entry list")
        self.assertIn("First Post", out)

        # 5. Add Comment
        out, err = self.run_cli(
            'python client/main.py comment add --entry-id 1 --content "hello!"'
        )
        self.assertIn("✅", out or err)

        # 6. List Comments
        out, err = self.run_cli("python client/main.py comment list --entry-id 1")
        self.assertIn("hello!", out)

    @classmethod
    def tearDownClass(cls):
        # Remove the token file after test
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)


if __name__ == "__main__":
    unittest.main()
