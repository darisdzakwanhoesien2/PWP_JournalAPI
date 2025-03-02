from extensions import db
from model_folder import User
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:

    @staticmethod
    def register_user(username, email, password):
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None  # User already exists

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    @staticmethod
    def get_user(user_id):
        return User.query.get(user_id)

    @staticmethod
    def update_user(user_id, username=None, email=None, password=None):
        user = User.query.get(user_id)
        if not user:
            return None

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = generate_password_hash(password)

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False