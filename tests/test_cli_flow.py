# tests/test_cli_flow.py
import os
import subprocess
import unittest
import re
import time
import multiprocessing
from app import create_app
from extensions import db
from journalapi.models import User, JournalEntry, Comment, EditHistory

from client.config import TOKEN_FILE

def run_flask_app():
    """Run the Flask app in a separate process."""
    app = create_app()
    app.run(host="localhost", port=8000, debug=False, use_reloader=False)

class TestJournalCLIFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask app in a separate process
        cls.flask_process = multiprocessing.Process(target=run_flask_app)
        cls.flask_process.start()
        # Wait for the server to start
        time.sleep(10)  # Increased from 5 to 10 seconds
        print("DEBUG [setUpClass] Flask server started")

        # Reset the database for a clean test environment
        app = create_app()
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("DEBUG [setUpClass] Database reset and initialized")

    @classmethod
    def tearDownClass(cls):
        # Terminate the Flask app process
        cls.flask_process.terminate()
        cls.flask_process.join()
        # Clean up token file
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        print("DEBUG [tearDownClass] Flask server terminated and token file cleaned")

    def run_cli(self, command):
        """
        Run a CLI command and return stdout and stderr as strings.
        """
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                env=dict(os.environ, PYTHONPATH=".", PYTHONIOENCODING="utf-8"),
                text=True,
                encoding='utf-8'
            )
            print(f"DEBUG [run_cli] Command: {command}")
            print(f"DEBUG [run_cli] stdout: {result.stdout}")
            print(f"DEBUG [run_cli] stderr: {result.stderr}")
            return result.stdout or "", result.stderr or ""
        except subprocess.CalledProcessError as e:
            print(f"DEBUG [run_cli] Command failed: {command}")
            print(f"DEBUG [run_cli] Exit code: {e.returncode}")
            print(f"DEBUG [run_cli] stderr: {e.stderr}")
            return "", e.stderr or ""

    def test_cli_end_to_end(self):
        # Use dynamic username and email to avoid conflicts
        timestamp = int(time.time())
        username = f"foo_{timestamp}"
        email = f"foo_{timestamp}@example.com"

        # 1. Register a new user
        command = f'python client/main.py auth register --username {username} --email {email} --password "testpass123"'
        out, err = self.run_cli(command)
        print(f"DEBUG [test_cli_end_to_end] Register stdout: {out}")
        print(f"DEBUG [test_cli_end_to_end] Register stderr: {err}")
        self.assertIn("✅", out + err, f"Registration failed: stdout: {out}, stderr: {err}")

        # 2. Login
        out, err = self.run_cli(
            f'python client/main.py auth login --email {email} --password "testpass123"'
        )
        print(f"DEBUG [test_cli_end_to_end] Login stdout: {out}")
        print(f"DEBUG [test_cli_end_to_end] Login stderr: {err}")
        self.assertIn("✅ Logged in", out + err, f"Login failed: stdout: {out}, stderr: {err}")
        self.assertTrue(os.path.exists(TOKEN_FILE), "Token file not found after login.")

        # 3. Create a journal entry
        out, err = self.run_cli(
            'python client/main.py entry create "First Post" "This is my first journal." --tags "test,cli"'
        )
        print(f"DEBUG [test_cli_end_to_end] Entry create stdout: {out}")
        print(f"DEBUG [test_cli_end_to_end] Entry create stderr: {err}")
        self.assertIn("✅", out + err, f"Entry creation failed: stdout: {out}, stderr: {err}")

        # 4. List entries and extract entry ID
        out, err = self.run_cli("python client/main.py entry list")
        print(f"DEBUG [test_cli_end_to_end] Entry list stdout: {out}")
        print(f"DEBUG [test_cli_end_to_end] Entry list stderr: {err}")
        self.assertIn("First Post", out, f"Entry list output did not include entry title: {out}")
        lines = out.strip().splitlines()
        entry_line = next((line for line in lines if "First Post" in line), None)
        self.assertIsNotNone(entry_line, "No entry line found in output.")
        match = re.search(r"\[(\d+)\]", entry_line)
        self.assertIsNotNone(match, f"Could not extract entry ID from line: {entry_line}")
        entry_id = match.group(1)

        # 5. Add a comment to the entry
        out, err = self.run_cli(f'python client/main.py comment add {entry_id} "hello!"')
        print(f"DEBUG [test_cli_end_to_end] Comment add stdout: {out}")
        print(f"DEBUG [test_cli_end_to_end] Comment add stderr: {err}")
        self.assertIn("✅", out + err, f"Comment add failed: stdout: {out}, stderr: {err}")

        # 6. List comments and verify the comment exists
        out, err = self.run_cli(f'python client/main.py comment list {entry_id}')
        print(f"DEBUG [test_cli_end_to_end] Comment list stdout: {out}")
        print(f"DEBUG [test_cli_end_to_end] Comment list stderr: {err}")
        self.assertIn("hello!", out, f"Comment 'hello!' not found in output: {out}")

if __name__ == "__main__":
    unittest.main()