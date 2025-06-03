# PWP_JournalAPI/init_db.py
"""Initialize the database for the Journal API."""
from app import create_app
from extensions import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with required tables."""
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

if __name__ == "__main__":
    init_database()