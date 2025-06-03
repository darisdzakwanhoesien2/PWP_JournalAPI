# PWP_JournalAPI/client/auth.py
"""Client authentication utilities for the Journal API CLI."""
import json
import logging
import os
from pathlib import Path
from typing import Optional

from client.config import TOKEN_FILE

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def save_token(token: str) -> None:
    """Save JWT token to a file for authenticated requests.

    Args:
        token: The JWT token to save.
    """
    try:
        Path(TOKEN_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"token": token, "saved_at": os.time()}, f)
        logger.info("Token saved successfully")
    except (OSError, json.JSONEncodeError) as e:
        logger.error("Failed to save token: %s", e)
        raise

def get_token() -> Optional[str]:
    """Retrieve the saved JWT token from file.

    Returns:
        The token string or None if not found or invalid.
    """
    if not os.path.exists(TOKEN_FILE):
        logger.debug("Token file not found")
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("token")
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Failed to read token: %s", e)
        return None

def clear_token() -> None:
    """Delete the stored JWT token to log out the user."""
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
            logger.info("Token cleared successfully")
        except OSError as e:
            logger.error("Failed to clear token: %s", e)
            raise

def get_auth() -> dict:
    """Return the authorization header if token exists.

    Returns:
        dict: Authorization header with bearer token or empty dict.
    """
    token = get_token()
    if token:
        logger.debug("Authorization header generated")
        return {"Authorization": f"Bearer {token}"}
    logger.debug("No token found, returning empty auth header")
    return {}