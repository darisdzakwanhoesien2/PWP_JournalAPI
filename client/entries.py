import requests
from .auth import get_auth
from .config import API_URL, REQUEST_TIMEOUT
from journalapi.utils import handle_error

def create_entry(title: str, content: str, tags: list):
    """Create a new journal entry."""
    try:
        response = requests.post(
            f"{API_URL}/entries",
            json={"title": title, "content": content, "tags": tags},
            headers=get_auth(),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return handle_error(response, e, "Failed to create entry")

def get_entry(entry_id: int):
    """Retrieve a journal entry by ID."""
    try:
        response = requests.get(
            f"{API_URL}/entries/{entry_id}",
            headers=get_auth(),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return handle_error(response, e, "Failed to fetch entry")