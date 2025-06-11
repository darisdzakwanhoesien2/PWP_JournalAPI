# PWP SPRING 2025 Journal API

---

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Database Setup](#database-setup)
    * [Running the API](#running-the-api)
    * [CLI Usage](#cli-usage)
4. [API Reference](#api-reference)
    * [Live Documentation](#live-documentation)
    * [Authentication](#authentication)
    * [Hypermedia \`_links\` ](#hypermedia-_links)
    * [Link Relations](#link-relations)
    * [API Endpoints](#api-endpoints)
    * [Error Handling](#error-handling)
5. [Development](#development)
    * [Dependencies](#dependencies)
    * [Testing](#testing)
    * [Contributing](#contributing)
6. [Deployment](#deployment)
    * [Docker Deployment](#docker-deployment)
7. [License and Contact Information](#license-and-contact-information)
    * [License](#license)
    * [Contact](#contact)
8. [Submission Checklist](#submission-checklist)

---

## Overview <a name="overview"></a>

The Journal API is a RESTful web service designed to help users manage daily journaling activities. It allows users to create, view, edit, and delete journal entries and interact with comments. The API is built using Flask and secured using JWTs.

---

## Key Features <a name="key-features"></a>

- ✅ **User Registration & Login** with hashed passwords
- ✅ **JWT Authentication**
- ✅ **CRUD Journal Entries** with tagging and history
- ✅ **Comments API** per entry
- ✅ **Modular Flask RESTful API**
- ✅ **Typer-based Python CLI** for users
- ✅ **Swagger UI** available at `/apidocs/`
- ✅ **Production-ready Docker deployment**
- ✅ **Optional Auxiliary Service** for analytics

---

## Getting Started <a name="getting-started"></a>

### Prerequisites <a name="prerequisites"></a>

- Python 3.6+
- Pip

### Installation <a name="installation"></a>

```bash
# Clone the repository
git clone https://github.com/darisdzakwanhoesien2/PWP_JournalAPI.git
cd PWP_JournalAPI

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### Database Setup <a name="database-setup"></a>

The API uses SQLite for database management. To initialize the database, run:

```bash
python init_db.py
```

This will create the necessary tables in the database. To populate the database with sample data, run:

```bash
python insert_from_files.py
```

### Running the API <a name="running-the-api"></a>

To start the API server, run:

```bash
flask --app app run --port=8000
```

The API will be available at `http://localhost:8000`.

### CLI Usage <a name="cli-usage"></a>

```bash
cd client/

# Register
python main.py auth register --username alice --email alice@example.com --password secure123

# Login
python main.py auth login --email alice@example.com --password secure123

# View entries
python main.py entry list

# Add entry
python main.py entry create --title "Test" --content "My first entry" --tags life,personal
```

---

## API Reference <a name="api-reference"></a>

### Live Documentation <a name="live-documentation"></a>

- **Swagger UI**: [http://localhost:8000/apidocs](http://localhost:8000/apidocs)
- **Raw OpenAPI YAML**: [`docs/openapi.yaml`](./docs/openapi.yaml)

### Authentication <a name="authentication"></a>

JWT Bearer Token in `Authorization` header:

```
Authorization: Bearer <token>
```

### Hypermedia `_links` <a name="hypermedia-_links"></a>

Embedded links allow clients to navigate between resources:

```json
{
  "id": 3,
  "title": "My Journal",
  "tags": ["reflection", "grateful"],
  "_links": {
    "self": { "href": "/entries/3" },
    "edit": { "href": "/entries/3" },
    "delete": { "href": "/entries/3" },
    "comments": { "href": "/entries/3/comments" },
    "history": { "href": "/entries/3/history" }
  }
}
```

### Link Relations <a name="link-relations"></a>

| Resource      | Link Relations                         |
|---------------|------------------------------------------|
| `User`        | `self`, `edit`, `delete`                |
| `JournalEntry`| `self`, `edit`, `delete`, `comments`, `history` |
| `Comment`     | `self`, `edit`, `delete`                |

### API Endpoints <a name="api-endpoints"></a>


### Error Handling <a name="error-handling"></a>

| Code | Meaning          | Example                      |
|------|------------------|------------------------------|
| 422  | Validation Error | Missing required field       |
|      |                  | Example: {"message": "The email field is required."} |
| 401  | Unauthorized     | Token missing or invalid     |
|      |                  | Example: {"message": "Authorization token is missing or invalid."} |
| 403  | Forbidden        | User not allowed             |
|      |                  | Example: {"message": "You do not have permission to access this resource."} |
| 404  | Not Found        | Resource doesn't exist       |
|      |                  | Example: {"message": "The requested resource was not found."} |

---

## Development <a name="development"></a>

### Dependencies <a name="dependencies"></a>

```bash
pip install -r requirements.txt
```

The Journal API relies on the following Python libraries:

- **Flask**, **SQLAlchemy**: Core web & ORM
- **Flask-JWT-Extended**: Token auth
- **Typer**, **Requests**: CLI client
- **Pytest**: Functional testing

### Testing <a name="testing"></a>

```bash
pytest --cov=journalapi tests/
```

### Contributing <a name="contributing"></a>

Contributions to the Journal API are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and ensure all tests pass.
4. Submit a pull request with a detailed description of your changes.

---

## Deployment <a name="deployment"></a>

### Docker Deployment <a name="docker-deployment"></a>

```bash
# Build and start containers
docker-compose up --build

# Init DB in container
docker-compose exec journal-api python init_db.py
```

---

## License and Contact Information <a name="license-and-contact-information"></a>

### License <a name="license"></a>

MIT License © 2025 Oulu PWP Team

### Contact <a name="contact"></a>

For feedback, contact the team at oulu.pwp@example.com

---

## Submission Checklist <a name="submission-checklist"></a>

- [x] REST API working
- [x] JWT Secured
- [x] Swagger & CLI
- [x] Docker Ready
- [x] Wiki + Mermaid Diagrams
- [x] Auxiliary Service Ready
- [x] Environment Variables Documented
- [x] Contributing Guidelines
- [x] Code of Conduct
- [x] Security Measures Documented
- [x] FAQ Section

---

## Contributing <a name="contributing"></a>

Contributions to the Journal API are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bugfix.
3.  Make your changes and ensure all tests pass.
4.  Submit a pull request with a detailed description of your changes.

---

## Code of Conduct <a name="code-of-conduct"></a>

This project adheres to the Contributor Covenant [code of conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to oulu.pwp@example.com.

---

## Environment Variables <a name="environment-variables"></a>

The following environment variables can be used to configure the application:

- `DATABASE_URL`: The URL of the database to use. Defaults to `sqlite:///instance/journal.db`.
- `JWT_SECRET_KEY`: The secret key used to sign JWT tokens. Defaults to a randomly generated string.
- `FLASK_DEBUG`: Enable or disable debug mode. Defaults to `False`.

---

## Security <a name="security"></a>

The Journal API uses JWTs for authentication and authorization. Passwords are hashed using bcrypt. The API is protected against common web vulnerabilities such as XSS and CSRF.

---

## FAQ <a name="faq"></a>

**Q: How do I run the API in development mode?**

A: Set the `FLASK_DEBUG` environment variable to `True`.

**Q: How do I contribute to the project?**

A: See the [Contributing](#contributing) section for more information.

---

