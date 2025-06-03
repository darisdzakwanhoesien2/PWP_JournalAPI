"""Test user-related endpoints."""
import json

def test_register_user(client):
    """Test user registration."""
    response = client.post('/api/users/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123'  # Must be at least 6 chars
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'User registered successfully'

def test_register_duplicate_email(client):
    """Test registering with duplicate email."""
    # First registration
    client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    # Second registration with same email
    response = client.post('/api/users/register', json={
        'username': 'user2',
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    # Update expected status code to match your API (400 for duplicate email)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Email already registered'

def test_login_user(client):
    """Test user login."""
    # Register first
    client.post('/api/users/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'loginpass123'
    })
    
    # Login
    response = client.post('/api/users/login', json={
        'email': 'login@example.com',
        'password': 'loginpass123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert '_links' in data

def test_get_user(client, auth_headers):
    """Test getting user details."""
    # First get the user ID from registration
    response = client.get('/api/users/1', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'username' in data
    assert 'email' in data
    assert data['username'] == 'testuser'  # From auth_headers fixture
    assert data['email'] == 'test@example.com'  # From auth_headers fixture

def test_update_user(client, auth_headers):
    """Test updating user details."""
    response = client.put('/api/users/1', json={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'password': 'updatedpass123'
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'User updated successfully'
    
    # Verify update
    get_resp = client.get('/api/users/1', headers=auth_headers)
    get_data = get_resp.get_json()
    assert get_data['username'] == 'updateduser'
    assert get_data['email'] == 'updated@example.com'

def test_delete_user(client, auth_headers):
    """Test deleting a user."""
    # Create a second user to test deletion
    register_resp = client.post('/api/users/register', json={
        'username': 'todelete',
        'email': 'delete@example.com',
        'password': 'deletepass123'
    })
    assert register_resp.status_code == 201
    
    # Login as second user
    login_resp = client.post('/api/users/login', json={
        'email': 'delete@example.com',
        'password': 'deletepass123'
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()['token']
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Delete user (assuming new user gets ID 2)
    delete_resp = client.delete('/api/users/2', headers=headers)
    assert delete_resp.status_code == 200
    delete_data = delete_resp.get_json()
    assert 'message' in delete_data
    assert delete_data['message'] == 'User deleted successfully'
    
    # Verify deletion
    get_resp = client.get('/api/users/2', headers=headers)
    assert get_resp.status_code == 404