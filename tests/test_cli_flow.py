"""Unit tests for CLI end-to-end flow."""
import os
import subprocess
import unittest
import re
import time
from client.config import TOKEN_FILE

class TestJournalCLIFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Reset the database for a clean test environment."""
        try:
            subprocess.run(["python", "init_db.py"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to initialize database: {e.stderr}") from e

    def run_cli(self, command):
        """Run a CLI command and return stdout and stderr as strings."""
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        return result.stdout, result.stderr

    def test_cli_end_to_end(self):
        """Test the full CLI workflow: register, login, create entry, comment, and list."""
        email = f"foo_{int(time.time())}@example.com"

        # 1. Register a new user
        out, err = self.run_cli(
            f'python client/main.py auth register --username foo --email {email} --password testpass123'
        )
        print("DEBUG [register] stdout:", out)
        print("DEBUG [register] stderr:", err)
        self.assertIn("✅", out or err, f"Registration failed: stdout: {out}, stderr: {err}")

        # 2. Login
        out, err = self.run_cli(
            f'python client/main.py auth login --email {email} --password testpass123'
        )
        print("DEBUG [login] stdout:", out)
        print("DEBUG [login] stderr:", err)
        self.assertIn("✅ Logged in", out or err, f"Login failed: stdout: {out}, stderr: {err}")
        self.assertTrue(os.path.exists(TOKEN_FILE), "Token file not found after login.")

        # 3. Create a journal entry
        out, err = self.run_cli(
            'python client/main.py entry create "First Post" "This is my first journal." --tags "test,cli"'
        )
        print("DEBUG [create_entry] stdout:", out)
        print("DEBUG [create_entry] stderr:", err)
        self.assertIn("✅", out or err, f"Entry creation failed: stdout: {out}, stderr: {err}")

        # 4. List entries and extract entry ID
        out, err = self.run_cli("python client/main.py entry list")
        print("DEBUG [list_entries] stdout:", out)
        print("DEBUG [list_entries] stderr:", err)
        self.assertIn("First Post", out, f"Entry list output did not include entry title: {out}")
        lines = out.strip().splitlines()
        entry_line = next((line for line in lines if "First Post" in line), None)
        self.assertIsNotNone(entry_line, "No entry line found in output.")
        match = re.search(r"\[(\d+)\]", entry_line)
        self.assertIsNotNone(match, "Could not extract entry ID from line: " + entry_line)
        entry_id = match.group(1)

        # 5. Add a comment to the entry
        out, err = self.run_cli(f'python client/main.py comment add {entry_id} "hello!"')
        print("DEBUG [add_comment] stdout:", out)
        print("DEBUG [add_comment] stderr:", err)
        self.assertIn("✅", out or err, f"Comment add failed: stdout: {out}, stderr: {err}")

        # 6. List comments and verify the comment exists
        out, err = self.run_cli(f"python client/main.py comment list {entry_id}")
        print("DEBUG [list_comments] stdout:", out)
        print("DEBUG [list_comments] stderr:", err)
        self.assertIn("hello!", out, f"Comment 'hello!' not found in output: {out}")

    @classmethod
    def tearDownClass(cls):
        """Clean up token file after tests."""
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

if __name__ == "__main__":
    unittest.main()

# # tests/test_cli_flow.py
# import os
# import subprocess
# import unittest
# import re
# import time
# from client.config import TOKEN_FILE

# class TestJournalCLIFlow(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # Reset the database for a clean test environment.
#         subprocess.run(["python", "init_db.py"], check=True)

#     def run_cli(self, command):
#         """
#         Run a CLI command and return stdout and stderr as strings.
#         """
#         result = subprocess.run(
#             command,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             shell=True,
#             env=dict(os.environ, PYTHONPATH="."),
#         )
#         return result.stdout.decode(), result.stderr.decode()

#     def test_cli_end_to_end(self):
#         # Use a dynamic email to avoid duplicate user conflicts.
#         email = f"foo_{int(time.time())}@example.com"

#         # 1. Register a new user
#         out, err = self.run_cli(
#             f'python client/main.py auth register --username foo --email {email} --password testpass123'
#         )
#         self.assertIn("✅", out or err, f"Registration failed: stdout: {out}, stderr: {err}")

#         # 2. Login
#         out, err = self.run_cli(
#             f'python client/main.py auth login --email {email} --password testpass123'
#         )
#         self.assertIn("✅ Logged in", out or err, f"Login failed: stdout: {out}, stderr: {err}")
#         self.assertTrue(os.path.exists(TOKEN_FILE), "Token file not found after login.")

#         # 3. Create a journal entry
#         out, err = self.run_cli(
#             'python client/main.py entry create "First Post" "This is my first journal." --tags "test,cli"'
#         )
#         self.assertIn("✅", out or err, f"Entry creation failed: stdout: {out}, stderr: {err}")

#         # 4. List entries and extract entry ID
#         out, err = self.run_cli("python client/main.py entry list")
#         self.assertIn("First Post", out, f"Entry list output did not include entry title: {out}")
#         lines = out.strip().splitlines()
#         entry_line = next((line for line in lines if "First Post" in line), None)
#         self.assertIsNotNone(entry_line, "No entry line found in output.")
#         match = re.search(r"\[(\d+)\]", entry_line)
#         self.assertIsNotNone(match, "Could not extract entry ID from line: " + entry_line)
#         entry_id = match.group(1)

#         # 5. Add a comment to the entry (using positional arguments)
#         out, err = self.run_cli(f'python client/main.py comment add {entry_id} "hello!"')
#         self.assertIn("✅", out or err, f"Comment add failed: stdout: {out}, stderr: {err}")

#         # 6. List comments and verify the comment exists (using the positional parameter for entry_id)
#         out, err = self.run_cli(f"python client/main.py comment list {entry_id}")
#         print("DEBUG: comment list stdout →", repr(out))
#         print("DEBUG: comment list stderr →", repr(err))
#         self.assertIn("hello!", out, f"Comment 'hello!' not found in output: {out}")

#     @classmethod
#     def tearDownClass(cls):
#         # Clean up token file after tests run.
#         if os.path.exists(TOKEN_FILE):
#             os.remove(TOKEN_FILE)

# if __name__ == "__main__":
#     unittest.main()
