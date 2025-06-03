"""Test CLI commands."""
from click.testing import CliRunner
from journalapi.cli import init_db_command
from extensions import db
import pytest

def test_init_db_command(app, db):
    """Test the init-db CLI command."""
    runner = CliRunner()
    
    # Drop all tables to simulate fresh state
    with app.app_context():
        db.drop_all()
    
    # Run the init-db command
    result = runner.invoke(init_db_command)
    
    assert result.exit_code == 0
    assert 'Initialized the database' in result.output
    
    # Verify tables were created
    with app.app_context():
        assert 'user' in db.metadata.tables
        assert 'journal_entry' in db.metadata.tables
        assert 'comment' in db.metadata.tables
        assert 'edit_history' in db.metadata.tables