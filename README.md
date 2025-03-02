# PWP SPRING 2025
# Journal API
# Group information
* Student 1. Muhammad Ramish (mramish24@student.oulu.fi)
* Student 2. Name and email
* Student 3. Name and email
* Student 4. Name and email

# Journal API

The Journal API is a RESTful web service designed to help users manage daily journaling activities. It allows users to create, view, edit, and delete journal entries, perform sentiment analysis on entries, and interact with comments on public or shared entries. The API is built using Flask, a lightweight Python web framework, and uses SQLite for database management.

---

## Features

- **User Management**: Register, log in, and manage user profiles.
- **Journal Entry Management**: Create, retrieve, update, and delete journal entries.
- **Sentiment Analysis**: Automatically analyze the emotional sentiment of journal entries.
- **Comment Management**: Add, retrieve, update, and delete comments on journal entries.
- **Authentication**: Secure access to resources using JWT (JSON Web Tokens).

---

## Table of Contents

1. [Installation](#installation)
2. [Database Setup](#database-setup)
3. [Running the API](#running-the-api)
4. [Testing](#testing)
5. [API Endpoints](#api-endpoints)
6. [Dependencies](#dependencies)
7. [Contributing](#contributing)
8. [License](#license)

---

## Installation

To set up the Journal API, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/darisdzakwanhoesien2/PWP_JournalAPI.git
   cd journal-api
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Database Setup

The API uses SQLite for database management. To initialize the database, run the following command:

```bash
python init_db.py
```

This will create the necessary tables in the database. To populate the database with sample data, run:

```bash
python insert_from_files.py
```

---

## Running the API

To start the API server, run:

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## Testing

The project includes a suite of functional tests to ensure the API works as expected. To run the tests, use the following commands:

```bash
python -m pytest tests/test_user_routes.py
python -m pytest tests/test_journal_entry_routes.py
python -m pytest tests/test_comments.py
```

These tests cover user management, journal entry management, and comment functionality.

---

## API Endpoints

The following table lists the available API endpoints:

| Resource Name       | Resource URL                          | Resource Description                                                                 | Supported Methods | Implemented |
|:-------------------:|:-------------------------------------:|:------------------------------------------------------------------------------------:|:-----------------:|:-----------:|
| User Management     | `/users/register`                     | Registers a new user with a username, email, and password.                           | POST              | Yes         |
|                     | `/users/login`                        | Authenticates a user and returns a JWT token for subsequent requests.                | POST              | Yes         |
|                     | `/users/{user_id}`                    | Retrieves, updates, or deletes a user's details based on the provided `user_id`.     | GET, PUT, DELETE  | Yes         |
| Journal Entry       | `/entries/`                           | Creates a new journal entry or retrieves all entries for the authenticated user.     | POST, GET         | Yes         |
|                     | `/entries/{entry_id}`                 | Retrieves, updates, or deletes a specific journal entry based on the `entry_id`.     | GET, PUT, DELETE  | Yes         |
| Comment Management  | `/entries/{entry_id}/comments`        | Adds a new comment to a journal entry or retrieves all comments for the entry.       | POST, GET         | Yes         |
|                     | `/comments/{comment_id}`              | Updates or deletes a specific comment based on the `comment_id`.                    | PUT, DELETE       | Yes         |

---

## Dependencies

The Journal API relies on the following Python libraries:

- **Flask**: Web framework for building the API.
- **Flask-SQLAlchemy**: ORM for database management.
- **Flask-JWT-Extended**: JWT-based authentication.
- **Pytest**: Testing framework for functional tests.

All dependencies are listed in `requirements.txt`.

---

## Contributing

Contributions to the Journal API are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and ensure all tests pass.
4. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or feedback, please contact Daris at [your.email@example.com].
```



