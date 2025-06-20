## current code
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_caching import Cache
from src.routes_users import users_bp
from src.routes_entries import entries_bp
from src.cache import cache

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this in production
    if app.testing:
        app.config["CACHE_TYPE"] = "NullCache"
    else:
        app.config["CACHE_TYPE"] = "SimpleCache"
        app.config["CACHE_DEFAULT_TIMEOUT"] = 300
    cache.init_app(app)
    jwt = JWTManager(app)

    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(entries_bp, url_prefix='/entries')

    @app.route('/login', methods=['POST'])
    def login():
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
