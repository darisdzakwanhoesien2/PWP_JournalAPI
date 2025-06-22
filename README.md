# Programmable Web Project - RESTful API

## Project Overview

This project implements a RESTful API for a discussion forum-like application. The API supports user management, entries (posts), comments, and edit history. It uses Flask, SQLAlchemy ORM, JWT authentication, and server-side caching.

The API follows REST principles and includes hypermedia links in responses for connectedness.

## Project Structure

- `src/`: Source code for the API
  - `app.py`: Main application factory and setup
  - `routes_users.py`: User-related API routes
  - `routes_entries.py`: Entry and comment-related API routes
  - `data_store.py`: Data loading and saving utilities
  - `models_orm.py`: SQLAlchemy ORM models
  - `cache.py`: Cache setup
  - `schemas.py`: Marshmallow schemas for validation
  - `utils.py`: Helper functions
- `tests/`: Functional tests for the API
- `documentation/`: Project documentation and state diagrams

## Setup and Installation

1. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the API server:

```bash
python src/app.py
```

The API will be available at `http://localhost:5000/`.

## Running Tests

Run the test suite with:

```bash
PYTHONPATH=. pytest --disable-warnings -v
```

This ensures the `src` package is found and all tests are executed.

## API Documentation

The API includes hypermedia links in responses for navigation. See the `documentation/` folder for detailed state diagrams and API design.

## Notes

- JWT authentication is used for protected endpoints.
- Server-side caching is implemented for GET requests.
- The database uses SQLite for simplicity.

## References

- Course: Programmable Web Project (PWP) Spring 2025
- Course Wiki: https://lovelace.oulu.fi/ohjelmoitava-web/pwp-spring-2025/
