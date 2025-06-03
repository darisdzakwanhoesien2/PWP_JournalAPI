# PWP_JournalAPI/docker_code.py
"""Generate OpenAPI specification for the Journal API."""
import os
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_openapi_yaml(output_path: str = "docs/openapi.yaml") -> None:
    """Generate and write OpenAPI 3.0 specification to a YAML file."""
    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "PWP Journal API",
            "description": "RESTful API for a journaling platform.",
            "version": "1.0.0"
        },
        "servers": [{"url": "/api"}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "paths": {
            "/users/register": {
                "post": {
                    "summary": "Register a new user",
                    "tags": ["Users"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["username", "email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "User created"},
                        "400": {"description": "Email or username already exists"},
                        "422": {"description": "Validation error"}
                    }
                }
            },
            "/users/login": {
                "post": {
                    "summary": "Login and retrieve a JWT token",
                    "tags": ["Users"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "JWT token returned"},
                        "401": {"description": "Invalid credentials"}
                    }
                }
            },
            "/journal_entries": {
                "get": {
                    "summary": "Get all journal entries for the current user",
                    "tags": ["Journal Entries"],
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {"description": "List of journal entries"}
                    }
                },
                "post": {
                    "summary": "Create a new journal entry",
                    "tags": ["Journal Entries"],
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "tags": {"type": "array", "items": {"type": "string"}}
                                    },
                                    "required": ["title", "content"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Entry created"},
                        "422": {"description": "Validation error"}
                    }
                }
            }
        }
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(openapi_spec, f, sort_keys=False)
    logger.info(f"OpenAPI spec written to {output_path}")

if __name__ == "__main__":
    generate_openapi_yaml()