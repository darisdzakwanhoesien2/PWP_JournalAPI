"""Database setup and sample data population."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models_orm import Base, User, Entry, Comment, EditHistory
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pwp_db.sqlite3')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_database():
    """Create database tables."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database tables created.")

def populate_database():
    """Populate the database with sample data."""
    session = Session()

    # Create sample users
    user1 = User(username='alice', email='alice@example.com', registered_at=datetime.utcnow())
    user2 = User(username='bob', email='bob@example.com', registered_at=datetime.utcnow())

    session.add_all([user1, user2])
    session.commit()

    # Create sample entries
    entry1 = Entry(user_id=user1.id, title='First Entry', content='Content of the first entry.')
    entry2 = Entry(user_id=user2.id, title='Second Entry', content='Content of the second entry.')

    session.add_all([entry1, entry2])
    session.commit()

    # Create sample comments
    comment1 = Comment(entry_id=entry1.id, user_id=user2.id, content='Nice entry!')
    comment2 = Comment(entry_id=entry2.id, user_id=user1.id, content='Thanks for sharing.')

    session.add_all([comment1, comment2])
    session.commit()

    # Create sample edit history
    edit1 = EditHistory(entry_id=entry1.id, edited_at=datetime.utcnow(), changes='{"title": {"old": "First Entry", "new": "Updated First Entry"}}')

    session.add(edit1)
    session.commit()

    session.close()
    print("Sample data populated.")

if __name__ == '__main__':
    create_database()
    populate_database()
