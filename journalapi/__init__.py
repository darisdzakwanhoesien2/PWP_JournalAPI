"""Initialize the Flask application for the Journal API."""
import os
from typing import Optional, Dict, Any
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from extensions import db
from journalapi import api
from journalapi.cli import init_db_command
from journalapi.extensions import jwt

load_dotenv()

def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        test_config: Configuration for testing.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", 
            f"sqlite:///{os.path.join(app.instance_path, 'journal.db')}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "test-secret-key")
    )

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_pyfile("config.py", silent=True)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(api.api_bp)
    app.cli.add_command(init_db_command)

    return app
