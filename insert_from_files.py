import csv
from app import create_app
from extensions import db
from journalapi.models import User, JournalEntry, EditHistory, Comment
from datetime import datetime, timezone
import json
from werkzeug.security import generate_password_hash

app = create_app()

def list_to_json(lst):
    return json.dumps(lst)

def insert_users(file_path):
    with open(file_path, "r") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            username, email, password = [field.strip() for field in row]
            if db.session.query(User).filter_by(email=email).first():
                print(f"⚠️ Skipping duplicate user: {email}")
                continue
            hashed_pw = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_pw)
            db.session.add(user)
        db.session.commit()
    print("✅ Users added successfully!")

def insert_journal_entries(file_path):
    """Reads journal entries from file and inserts them into the database."""
    with open(file_path, "r") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            user_id, title, content, tags, sentiment_score, sentiment_tag = row
            entry = JournalEntry(
                user_id=int(user_id),
                title=title.strip(),
                content=content.strip(),
                tags=list_to_json([tag.strip() for tag in tags.split(",")]),
                sentiment_score=float(sentiment_score),
                sentiment_tag=list_to_json([tag.strip() for tag in sentiment_tag.split(",")]),
                last_updated=datetime.now(timezone.UTC)  # Already updated
            )
            db.session.add(entry)
        db.session.commit()
    print("✅ Journal Entries added successfully!")

def insert_edit_history(file_path):
    """Reads edit history from file and inserts them into the database."""
    with open(file_path, "r") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            journal_entry_id, user_id, previous_content, new_content = row
            edit = EditHistory(
                journal_entry_id=int(journal_entry_id),
                user_id=int(user_id),
                edited_at=datetime.now(timezone.UTC),  # Already updated
                previous_content=previous_content.strip(),
                new_content=new_content.strip()
            )
            db.session.add(edit)
        db.session.commit()
    print("✅ Edit History added successfully!")

def insert_comments(file_path):
    """Reads comments from file and inserts them into the database."""
    with open(file_path, "r") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                print(f"⚠️ Skipping invalid row (not enough fields): {row}")
                continue

            journal_entry_id = int(row[0])
            user_id = int(row[1])
            content = ",".join(row[2:]).strip()  # Fix: Join all remaining parts as comment text

            comment = Comment(
                journal_entry_id=journal_entry_id,
                user_id=user_id,
                content=content,
                timestamp=datetime.now(timezone.UTC)  # Updated
            )
            db.session.add(comment)

        db.session.commit()
    print("✅ Comments added successfully!")

if __name__ == "__main__":
    insert_users("data/users.txt")
    insert_journal_entries("data/journal_entries.txt")
    insert_edit_history("data/edit_history.txt")
    insert_comments("data/comments.txt")
    print("🎉 All data has been inserted successfully!")