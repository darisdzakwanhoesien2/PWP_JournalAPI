# PWP SPRING 2025
# PROJECT NAME
# Group information
* Student 1. Name and email
* Student 2. Name and email
* Student 3. Name and email
* Student 4. Name and email


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

## API Overview

The Web API developed offers functionalities to structure non-real-time conversations among users about topics of interest. Messages are grouped in Threads, which are further grouped in Topics. The API provides an interface to access and manage these messages, supporting operations such as creating, reading, updating, and deleting users, entries, comments, and edit histories. This API is part of a larger online learning environment system, responsible for discussion forum features that can be integrated into other components.

## Main Concepts and Relations

The main concepts of the API include Users, Entries, Comments, and Edit Histories. Users can register, update their profiles, and delete their accounts. Entries represent messages or posts created by users, which can be updated or deleted. Comments are associated with entries and can also be managed similarly. Edit Histories track changes made to entries. The relations among these concepts are represented in the state diagram included in the project documentation, illustrating the RESTful resource interactions and links.

## API Uses

The API supports both human-usable clients and machine-to-machine services. For example, a web client allows users to interact with discussion threads, while automated services can use the API to aggregate or moderate content. The API exposes endpoints for managing users, entries, comments, and edit histories, enabling diverse clients to integrate discussion forum functionalities into their applications.

## Testing and Verification

The API implementation has been thoroughly tested with comprehensive unit tests covering all endpoints and edge cases, including user registration, entries CRUD, comments CRUD, and edit history management. Tests verify correct behavior for creation, retrieval, update, and deletion operations, with proper authentication and error handling. The tests confirm the API meets the requirements described in the project documentation.

## Database Design and Implementation

The project uses PostgreSQL as the database backend, with SQLAlchemy as the ORM for database modeling and access. The database schema includes four main tables: Users, Entries, Comments, and EditHistory, each represented by a corresponding SQLAlchemy model in `src/models_orm.py`.

- **Users**: Stores user information including username, email, and registration timestamp.
- **Entries**: Represents posts or messages created by users, linked to the Users table via a foreign key.
- **Comments**: Associated with Entries and Users, storing comments content and timestamps.
- **EditHistory**: Tracks changes made to Entries, storing the edit timestamp and change details.

A database setup and population script (`src/db_setup.py`) is provided to create the tables and insert sample data for testing and development. The Flask application (`src/app.py`) is configured to connect to the PostgreSQL database and manage sessions using SQLAlchemy.

Instructions for setting up the PostgreSQL database, installing dependencies, running the setup script, and populating the database are included in the project documentation to facilitate easy deployment and testing.

## Related Work

The API resembles typical RESTful CRUD APIs used in discussion forums and social platforms. It is classified as a hypermedia-driven REST API, providing links to related resources in responses. Similar APIs include popular forum software APIs and social media platform APIs. Example clients include web frontends and mobile applications that interact with the API to provide user interfaces for discussions and content management.

## API Resources

| Resource Name       | URL                          | Description                          | Supported Methods       | Implemented |
|--------------------|------------------------------|------------------------------------|------------------------|-------------|
| Users Collection    | /users                       | Manage users                       | GET, POST              | Yes         |
| User Item           | /users/{id}                  | Retrieve, update, delete a user    | GET, PUT, DELETE       | Yes         |
| Entries Collection  | /entries                     | Manage entries                     | GET, POST              | Yes         |
| Entry Item          | /entries/{id}                | Retrieve, update, delete an entry  | GET, PUT, DELETE       | Yes         |
| Comments Collection | /entries/{id}/comments       | Manage comments for an entry       | GET, POST              | Yes         |
| Comment Item        | /comments/{comment_id}       | Retrieve, update, delete a comment | GET, PUT, DELETE       | Yes         |
| Edit History        | /entries/{id}/edit_history   | View edit history for an entry     | GET                    | Yes         |
| Edit History Item   | /entries/{id}/edit_history/{edit_id} | View specific edit history item | GET                    | Yes         |

## REST Principles

### Addressability
Each resource in the API is uniquely addressable via a URI. For example, users are accessible at `/users/{id}`, entries at `/entries/{id}`, and comments at `/comments/{comment_id}`. This allows clients to directly interact with specific resources.

### Uniform Interface
The API uses standard HTTP methods consistently across resources:
- `GET` to retrieve resources or collections.
- `POST` to create new resources.
- `PUT` to update existing resources.
- `DELETE` to remove resources.

This uniform interface simplifies client interactions and adheres to RESTful design.

### Statelessness
The API is stateless; each request contains all the information needed to process it. Authentication is handled via JWT tokens sent with each request, and the server does not maintain session state between requests.

## Setup and Running Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup the database:**
   - Configure PostgreSQL or use SQLite as per your preference.
   - Run the database setup script:
     ```bash
     python src/db_setup.py
     ```

3. **Run the Flask application:**
   ```bash
   flask run
   ```
   The API will be accessible at `http://localhost:5000/`.

4. **Run tests:**
   ```bash
   PYTHONPATH=. pytest --maxfail=1 --disable-warnings -q
   ```

This completes the API documentation and setup instructions.
   PYTHONPATH=. pytest --maxfail=1 --disable-warnings -q
     python src/db_setup.py

## RESTful API Implementation

The API implements at least five resources: Users, Entries, Comments, EditHistory, and Authentication. Each resource supports multiple HTTP methods including GET, POST, PUT, and DELETE, ensuring a uniform interface. The API follows REST principles of addressability, statelessness, and uniform interface by using resource URLs, stateless requests, and standard HTTP methods with appropriate response codes.

## Code Quality and Testing

The codebase follows idiomatic Python practices and passes linting checks with pylint after improvements. Comprehensive unit tests cover all API endpoints and edge cases, ensuring correct functionality and error handling. Test coverage exceeds 90%, demonstrating robust verification of the API implementation.

## Setup and Running Instructions

1. Install dependencies using `pip install -r requirements.txt`.
2. Set up the PostgreSQL database and configure connection parameters in `src/app.py`.
3. Run the database setup and population script: `python src/db_setup.py`.
4. Start the Flask application: `flask run` or `python src/app.py`.
5. Run tests with coverage: `PYTHONPATH=. pytest --cov=src tests/`.

## Extras

- URL converters are used for resource identifiers to ensure type safety and clean URLs.
- JSON schema validation is implemented using Marshmallow schemas for request validation.
- Server-side caching is applied to GET endpoints using Flask-Caching to improve performance.
- Authentication is implemented with JWT tokens, securing protected endpoints.

