import click
from flask.cli import with_appcontext
from journalapi import create_app, db
import secrets

@click.command("init-db")
@with_appcontext
def init_db_command():
    app = create_app()
    with app.app_context():
        db.create_all()
        click.echo("Initialized the database.")

@click.command("masterkey")
@with_appcontext
def masterkey_command():
    key = secrets.token_urlsafe(32)
    click.echo(f"Generated master key: {key}")