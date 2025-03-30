import click
from flask.cli import with_appcontext
from .models import db

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create all tables."""
    db.create_all()
    click.echo("Initialized the database.")
