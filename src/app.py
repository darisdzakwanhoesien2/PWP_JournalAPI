## current code
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_caching import Cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.routes_users import users_bp
from src.routes_entries import entries_bp
from src.cache import cache
from src.models_orm import Base

"""
Main application factory and setup for the Flask API.
"""

def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this in production
    if app.testing:
        app.config["CACHE_TYPE"] = "NullCache"
    else:
        app.config["CACHE_TYPE"] = "SimpleCache"
        app.config["CACHE_DEFAULT_TIMEOUT"] = 300
    cache.init_app(app)

    # SQLAlchemy setup
    DATABASE_URL = "postgresql://user:password@localhost:5432/pwp_db"  # Update with actual credentials or env var
    DATABASE_URL = "sqlite:///pwp_db.sqlite3"  # Updated to use SQLite for easier setup
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    app.db_session = scoped_session(session_factory)

    jwt = JWTManager(app)

    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(entries_bp, url_prefix='/entries')

    @app.teardown_appcontext
    def remove_session(exception=None):
        """
        Remove the database session at the end of the request or app context.
        """
        app.db_session.remove()

    @app.route('/login', methods=['POST'])
    def login():
        """
        Simple login endpoint to create JWT access token.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify({"msg": "Missing username parameter"}), 400
        username = data['username']
        # For demo, accept any username and create token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
