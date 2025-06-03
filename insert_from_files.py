# PWP_JournalAPI/insert_from_files.py
"""Insert data from CSV files into the Journal API database."""
import csv
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from app import create_app
from extensions import db
from journalapi.models import User, JournalEntry, EditHistory, Comment
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

def list_to_json(lst: list) -> str:
    """Convert a list to JSON string."""
    return json.dumps(lst)

def insert_users(file_path: Path) -> None:
    """Insert users from a CSV file."""
    with open(file_path, "r", encoding="utf-8") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                logger.warning(f"Skipping invalid row: {row}")
                continue
            username, email, password = [field.strip() for field in row]
            if db.session.query(User).filter_by(email=email).first():
                logger.warning(f"Skipping duplicate user: {email}")
                continue
            hashed_pw = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_pw)
            db.session.add(user)
        db.session.commit()
        logger.info("Users inserted successfully")

def insert_journal_entries(file_path: Path) -> None:
    """Insert journal entries from a CSV file."""
    with open(file_path, "r", encoding="utf-8") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 6:
                logger.warning(f"Skipping invalid row: {row}")
                continue
            user_id, title, content, tags, sentiment_score, sentiment_tag = row
            entry = JournalEntry(
                user_id=int(user_id),
                title=title.strip(),
                content=content.strip(),
                tags=list_to_json([tag.strip() for tag in tags.split(",")]),
                sentiment_score=float(sentiment_score),
                sentiment_tag=list_to_json([tag.strip() for tag in sentiment_tag.split(",")]),
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(entry)
        db.session.commit()
        logger.info("Journal entries inserted successfully")

def insert_edit_history(file_path: Path) -> None:
    """Insert edit history from a CSV file."""
    with open(file_path, "r", encoding="utf-8") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 4:
                logger.warning(f"Skipping invalid row: {row}")
                continue
            journal_entry_id, user_id, previous_content, new_content = row
            edit = EditHistory(
                journal_entry_id=int(journal_entry_id),
                user_id=int(user_id),
                edited_at=datetime.now(timezone.utc),
                old_content=previous_content.strip(),
                new_content=new_content.strip()
            )
            db.session.add(edit)
        db.session.commit()
        logger.info("Edit history inserted successfully")

def insert_comments(file_path: Path) -> None:
    """Insert comments from a CSV file."""
    with open(file_path, "r", encoding="utf-8") as file, app.app_context():
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                logger.warning(f"Skipping invalid row: {row}")
                continue
            journal_entry_id, user_id, *content_parts = row
            content = ",".join(content_parts).strip()
            comment = Comment(
                journal_entry_id=int(journal_entry_id),
                user_id=int(user_id),
                content=content,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(comment)
        db.session.commit()
        logger.info("Comments inserted successfully")

if __name__ == "__main__":
    data_dir = Path("data")
    insert_users(data_dir / "users.txt")
    insert_journal_entries(data_dir / "journal_entries.txt")
    insert_edit_history(data_dir / "edit_history.txt")
    insert_comments(data_dir / "comments.txt")
    logger.info("All data inserted successfully")