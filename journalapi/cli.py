import click
from flask.cli import with_appcontext
from . import db
from . import models

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo("Initialized the database.")