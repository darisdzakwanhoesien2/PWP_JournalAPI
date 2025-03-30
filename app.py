import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# We'll import the blueprint from journalapi.api
# and also the CLI from journalapi.cli
from journalapi.api import api_bp
from journalapi.cli import init_db_command

# Create a single DB instance globally
db = SQLAlchemy()

def create_app(test_config=None):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)

    # Provide a default config (used in dev)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "journal.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # If test config is given, override defaults
    if test_config:
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    JWTManager(app)

    # Register blueprint with optional prefix. 
    # If you want routes at /api/... add url_prefix="/api".
    app.register_blueprint(api_bp)

    # Register CLI command for init-db
    app.cli.add_command(init_db_command)

    return app
