# PWP_JournalAPI/client/utils.py
"""Utility functions for the Journal API CLI."""
import logging

import requests
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

def handle_error(res: requests.Response, error: Exception, message: str) -> None:
    """Handle HTTP request errors and display appropriate messages.

    Args:
        res: The HTTP response object.
        error: The exception raised.
        message: The error message to display.
    """
    try:
        err = res.json()
        console.print(
            f"[red]❌ {message}: {err.get('error', err.get('errors', 'Unknown error'))}[/red]"
        )
        logger.error("%s: %s", message, err)
    except (requests.JSONDecodeError, ValueError):
        console.print(f"[red]❌ Server error: {res.text}[/red]")
        logger.error("%s: %s, %s", message, res.text, error)