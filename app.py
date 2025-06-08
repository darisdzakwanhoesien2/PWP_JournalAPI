# PWP_JournalAPI/app.py
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from extensions import db
from journalapi.api import api_bp
from journalapi.cli import init_db_command
from journalapi.utils import json_response  # ✅ Custom response utility

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DEBUG=bool(os.environ.get("DEBUG", "False") == "True"),
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///" + os.path.join(app.instance_path, "journal.db")
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SWAGGER={"title": "PWP Journal API", "uiversion": 3}
    )

    if test_config:
        app.config.update(test_config)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)

    # ✅ Load OpenAPI spec from file
    Swagger(app, template_file="docs/openapi.yaml")

    # ✅ Add a root health-check route
    @app.route("/")
    def root():
        return json_response({"message": "✅ Journal API is running!"}, 200)

    # Register blueprint and CLI command
    app.register_blueprint(api_bp)
    app.cli.add_command(init_db_command)

    return app
