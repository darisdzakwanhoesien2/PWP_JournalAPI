from extensions import db
import json 

def list_to_json(lst):
    return json.dumps(lst)

def json_to_list(json_str):
    return json.loads(json_str) if json_str else []


class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    journal_entries = db.relationship("JournalEntry", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    edit_history = db.relationship("EditHistory", back_populates="editor", cascade="all, delete-orphan")
