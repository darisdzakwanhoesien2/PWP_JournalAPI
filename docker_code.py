import os

# Create the docs directory if it doesn't exist
os.makedirs("docs", exist_ok=True)

# Define the Swagger 2.0 openapi.yaml content
openapi_yaml_content = """swagger: "2.0"
info:
  title: PWP Journal API
  description: API documentation for the journaling platform.
  version: "1.0"
host: localhost:8000
basePath: /
schemes:
  - http
consumes:
  - application/json
produces:
  - application/json
securityDefinitions:
  BearerAuth:
    type: apiKey
    name: Authorization
    in: header
    description: >
      JWT Authorization header using the Bearer scheme.
      Example: "Authorization: Bearer {token}"
paths:
  /users/register:
    post:
      summary: Register a new user
      tags:
        - Users
      parameters:
        - in: body
          name: user
          description: User registration data
          required: true
          schema:
            type: object
            properties:
              username:
                type: string
              email:
                type: string
              password:
                type: string
      responses:
        201:
          description: User created successfully
        400:
          description: Email or username already exists
        422:
          description: Validation error
  /users/login:
    post:
      summary: Login and retrieve a JWT token
      tags:
        - Users
      parameters:
        - in: body
          name: credentials
          description: User login data
          required: true
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
      responses:
        200:
          description: JWT token returned
        401:
          description: Invalid credentials
  /entries/:
    get:
      summary: Get all journal entries for the current user
      tags:
        - Journal Entries
      security:
        - BearerAuth: []
      responses:
        200:
          description: A list of journal entries
    post:
      summary: Create a new journal entry
      tags:
        - Journal Entries
      security:
        - BearerAuth: []
      parameters:
        - in: body
          name: entry
          required: true
          schema:
            type: object
            properties:
              title:
                type: string
              content:
                type: string
              tags:
                type: array
                items:
                  type: string
      responses:
        201:
          description: Entry created
        422:
          description: Validation error
"""

# Write the content to docs/openapi.yaml
with open("docs/openapi.yaml", "w") as f:
    f.write(openapi_yaml_content)

