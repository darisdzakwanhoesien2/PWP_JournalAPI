# app.py
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from extensions import db
from journalapi.api import api_bp
from journalapi.cli import init_db_command

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "journal.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Ensure instance dir
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(api_bp)
    app.cli.add_command(init_db_command)

    return app
