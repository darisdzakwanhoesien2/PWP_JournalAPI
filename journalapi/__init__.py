import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "journal.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if config:
        app.config.update(config)
    else:
        app.config.from_pyfile("config.py", silent=True)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    with app.app_context():
        db.init_app(app)
        jwt.init_app(app)

    # Register API blueprint
    from journalapi.api import api_bp
    app.register_blueprint(api_bp)

    # Register CLI commands
    from journalapi.cli import init_db_command, masterkey_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(masterkey_command)

    return app