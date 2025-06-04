#!/usr/bin/env python3
"""Debug script to test API endpoints."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from journalapi import create_app
from journalapi.models import User
from werkzeug.security import generate_password_hash
from extensions import db

def test_api():
    """Test the API endpoints to debug issues."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        
        client = app.test_client()
        
        # Test login
        print("Testing login...")
        response = client.post("/api/users/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        print(f"Login status: {response.status_code}")
        print(f"Login response: {response.get_json()}")
        
        if response.status_code == 200:
            token = response.json["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test get entries
            print("\nTesting get entries...")
            response = client.get("/api/journal_entries", headers=headers)
            print(f"Get entries status: {response.status_code}")
            print(f"Get entries response: {response.get_json()}")
            
            # Test create entry
            print("\nTesting create entry...")
            response = client.post("/api/journal_entries", json={
                "title": "Test Entry",
                "content": "Test Content",
                "tags": ["test"]
            }, headers=headers)
            print(f"Create entry status: {response.status_code}")
            print(f"Create entry response: {response.get_json()}")

if __name__ == "__main__":
    test_api()
