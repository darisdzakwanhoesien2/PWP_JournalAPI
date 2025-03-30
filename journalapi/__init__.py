# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# import os

# db = SQLAlchemy()

# def create_app(test_config=None):
#     app = Flask(__name__, instance_relative_config=True)
    
#     # Default config (used for development)
#     app.config.from_mapping(
#         SECRET_KEY="dev",
#         SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "journal.db"),
#         SQLALCHEMY_TRACK_MODIFICATIONS=False
#     )

#     # If test config is provided, override default
#     if test_config:
#         app.config.update(test_config)
#     else:
#         app.config.from_pyfile("config.py", silent=True)

#     try:
#         os.makedirs(app.instance_path, exist_ok=True)
#     except OSError:
#         pass

#     db.init_app(app)
#     JWTManager(app)

#     from . import api
#     app.register_blueprint(api.api_bp)

#     from .cli import init_db_command
#     app.cli.add_command(init_db_command)

#     return app
