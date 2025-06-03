# PWP_JournalAPI/journalapi/cli.py
"""Command-line interface commands for the Journal API."""
import click
from flask.cli import with_appcontext
from extensions import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database with required tables."""
    try:
        db.create_all()
        click.echo("Initialized the database.")
        logger.info("Database initialized via CLI")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise