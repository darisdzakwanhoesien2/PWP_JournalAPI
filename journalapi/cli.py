# PWP_JournalAPI/journalapi/cli.py
"""Command-line interface commands for the Journal API."""
import click
from flask.cli import with_appcontext
from extensions import db

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database with required tables."""
    db.create_all()
    click.echo("Initialized the database.")
