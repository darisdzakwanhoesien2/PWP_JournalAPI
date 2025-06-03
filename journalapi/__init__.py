# PWP_JournalAPI/journalapi/__init__.py
"""Initialize the Flask application for the Journal API."""
import logging
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from extensions import db
from journalapi.api import api_bp
from journalapi.cli import init_db_command

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """Create and configure the Flask application.

    Args:
        test_config (dict, optional): Configuration for testing.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(app.instance_path, 'journal.db')}",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "jwt-secret"),
    )

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_pyfile("config.py", silent=True)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as e:
        logger.error("Failed to create instance folder: %s", e)
        raise

    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.cli.add_command(init_db_command)

    logger.info("Flask application initialized")
    return app