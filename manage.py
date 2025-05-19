#!/usr/bin/env python
# manage.py

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()  # Runs the Flask development server (not for production)
