# journalapi/cli.py
import click
from flask.cli import with_appcontext

from extensions import db

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo("Initialized the database.")
