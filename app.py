from flask import Flask
from flask_jwt_extended import JWTManager
from extensions import db
from routes.user_routes import user_bp
from routes.journal_entry_routes import journal_entry_bp
from routes.comment_routes import comment_bp  # ✅ FIXED: Uncommented

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///journal.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "user123"  # Change this to a secure key in production

    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(journal_entry_bp, url_prefix="/entries")
    app.register_blueprint(comment_bp)  # ✅ FIXED: Register comment routes: , url_prefix="/comments"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
