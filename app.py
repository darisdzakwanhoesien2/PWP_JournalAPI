# app.py
from flask import Flask
from flask_jwt_extended import JWTManager
from extensions import db

def create_app(test_config=None):
    app = Flask(__name__)
    # Provide a default config
    app.config.from_mapping(
        TESTING=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///journal.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="user123"
    )

    # If test config is given, override
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    JWTManager(app)

    # Register blueprints
    from routes.user_routes import user_bp
    from routes.journal_entry_routes import journal_entry_bp
    from routes.comment_routes import comment_bp
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(journal_entry_bp, url_prefix="/entries")
    app.register_blueprint(comment_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
