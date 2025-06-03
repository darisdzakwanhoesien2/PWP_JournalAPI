"""Command-line interface commands for the Journal API."""
import logging

import click
from flask.cli import with_appcontext
from extensions import db

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
        logger.error("Failed to initialize database: %s", e)
        raise
