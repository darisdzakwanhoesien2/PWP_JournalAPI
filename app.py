# PWP_JournalAPI/app.py
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from extensions import db
from journalapi.api import api_bp
from journalapi.cli import init_db_command
from journalapi.utils import JsonResponse  # ✅ Add this for unified responses

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DEBUG=True,
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "journal.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SWAGGER={"title": "PWP Journal API", "uiversion": 3}
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    JWTManager(app)
    Swagger(app, template_file="docs/openapi.yaml")

    # ✅ Root health-check route
    @app.route("/")
    def root():
        return JsonResponse({"message": "✅ Journal API is running!"}, 200)

    app.register_blueprint(api_bp)
    app.cli.add_command(init_db_command)

    return app
