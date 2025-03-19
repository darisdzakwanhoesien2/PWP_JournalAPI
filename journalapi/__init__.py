import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "journal.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile("config.py", silent=True)

    os.makedirs(app.instance_path, exist_ok=True)

    print("DB INIT")
    db.init_app(app)
    jwt = JWTManager(app)

    from . import models
    with app.app_context():
        db.create_all()

    print("API")
    from . import api
    app.register_blueprint(api.api_bp)


    return app
