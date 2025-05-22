"""Initialize the Flask application for the Journal API."""
from flask import Flask
from journalapi.api import api_bp
from extensions import db

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///journal.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
