# PWP_JournalAPI/app.py
import os
import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from dotenv import load_dotenv
from extensions import db
from journalapi.api import api_bp
from journalapi.cli import init_db_command
from journalapi.utils import json_response

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        DEBUG=False,  # Disable debug in production
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),  # Use env var for security
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'journal.db')}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "jwt-secret"),  # Separate JWT key
        SWAGGER={"title": "PWP Journal API", "uiversion": 3, "version": "1.0.0"}
    )

    # Override with test config if provided
    if test_config:
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create instance folder: {e}")
        raise

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    Swagger(app, template_file="docs/openapi.yaml")

    # Health-check route
    @app.route("/")
    def root():
        logger.info("Health check accessed")
        return json_response({"message": "PWP Journal API is running", "status": "healthy"}, 200)

    # Register blueprint and CLI command
    app.register_blueprint(api_bp, url_prefix="/api")
    app.cli.add_command(init_db_command)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))