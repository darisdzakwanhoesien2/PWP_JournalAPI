# PWP_JournalAPI/tests/test_cli.py
import unittest
from click.testing import CliRunner
from journalapi.cli import init_db_command
from app import create_app
from extensions import db
from sqlalchemy import inspect  # Added import

class TestCli(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.runner = CliRunner()

    def test_init_db_command(self):
        with self.app.app_context():
            result = self.runner.invoke(init_db_command)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Initialized the database", result.output)
            # Verify tables were created
            self.assertTrue(inspect(db.engine).has_table("users"))  # Updated

if __name__ == "__main__":
    unittest.main()