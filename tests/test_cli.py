# tests/test_cli.py
"""Tests for CLI commands."""
import pytest
from click.testing import CliRunner
from journalapi.cli import init_db_command
from extensions import db

def test_init_db_command(app):
    """Test init_db_command."""
    runner = CliRunner()
    with app.app_context():
        result = runner.invoke(init_db_command)
        assert result.exit_code == 0
        assert "Initialized the database." in result.output
        # Verify tables exist
        assert db.metadata.tables.get("user") is not None