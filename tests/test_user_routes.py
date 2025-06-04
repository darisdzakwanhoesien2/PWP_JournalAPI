import json
import re

def test_register_user(client):
    """Test user registration."""
    response = client.post('/api/users/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123'
    })
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.get_data(as_text=True)}"
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'User registered successfully'
    assert 'user' in data
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'new@example.com'
    assert '_links' in data
    assert 'self' in data['_links']
    assert re.match(r'/api/users/\d+', data['_links']['self'])

def test_register_duplicate_email(client):
    """Test registering with duplicate email."""
    response = client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    
    response = client.post('/api/users/register', json={
        'username': 'user2',
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Email already registered'

def test_register_duplicate_username(client):
    """Test registering with duplicate username."""
    response = client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    
    response = client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'user2@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Username already registered'

def test_register_invalid_password(client):
    """Test registering with a password that's too short."""
    response = client.post('/api/users/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': '123'
    })
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'error' in data
    assert 'password' in data['error']
    assert 'Shorter than minimum length' in str(data['error'])

def test_register_invalid_email(client):
    """Test registering with an invalid email format."""
    response = client.post('/api/users/register', json={
        'username': 'newuser',
        'email': 'invalid-email',
        'password': 'newpass123'
    })
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'error' in data
    assert 'email' in data['error']
    assert 'Invalid email' in str(data['error'])

def test_register_missing_fields(client):
    """Test registering with missing fields."""
    response = client.post('/api/users/register', json={
        'username': 'newuser',
        # Missing email and password
    })
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'error' in data
    assert 'email' in data['error']
    assert 'password' in data['error']

def test_login_user(client):
    """Test user login."""
    response = client.post('/api/users/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'loginpass123'
    })
    assert response.status_code == 201
    
    response = client.post('/api/users/login', json={
        'email': 'login@example.com',
        'password': 'loginpass123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert isinstance(data['token'], str)
    assert len(data['token'].split('.')) == 3  # Basic JWT format check
    assert '_links' in data
    assert 'self' in data['_links']
    assert re.match(r'/api/users/\d+', data['_links']['self'])

def test_login_invalid_credentials(client):
    """Test login with incorrect password."""
    response = client.post('/api/users/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'loginpass123'
    })
    assert response.status_code == 201
    
    response = client.post('/api/users/login', json={
        'email': 'login@example.com',
        'password': 'wrongpass'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid credentials' in data['error']

def test_login_non_existent_user(client):
    """Test login with non-existent email."""
    response = client.post('/api/users/login', json={
        'email': 'nonexistent@example.com',
        'password': 'anypass123'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid credentials' in data['error']

def test_get_user(client, auth_headers):
    """Test getting user details."""
    # Register a new user to avoid relying on auth_headers user
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    user_id = response.get_json()['user']['id']
    
    # Login to get token
    login_resp = client.post('/api/users/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()['token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = client.get(f'/api/users/{user_id}', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'username' in data
    assert 'email' in data
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'
    assert '_links' in data
    assert data['_links']['self'] == f'/api/users/{user_id}'

def test_get_user_not_found(client, auth_headers):
    """Test getting a non-existent user."""
    response = client.get('/api/users/999', headers=auth_headers)
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'User not found' in data['error']

def test_get_user_unauthorized(client, auth_headers):
    """Test getting another user's details."""
    # Register user1
    response = client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'pass123'
    })
    assert response.status_code == 201
    user1_id = response.get_json()['user']['id']
    
    # Register user2 and get token
    response = client.post('/api/users/register', json={
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'pass123'
    })
    assert response.status_code == 201
    login_resp = client.post('/api/users/login', json={
        'email': 'user2@example.com',
        'password': 'pass123'
    })
    assert login_resp.status_code == 200
    user2_token = login_resp.get_json()['token']
    user2_headers = {
        'Authorization': f'Bearer {user2_token}',
        'Content-Type': 'application/json'
    }
    
    response = client.get(f'/api/users/{user1_id}', headers=user2_headers)
    
    assert response.status_code == 403
    data = response.get_json()
    assert 'error' in data
    assert 'Unauthorized' in data['error']

def test_update_user(client, auth_headers):
    """Test updating user details."""
    # Register a new user
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    user_id = response.get_json()['user']['id']
    
    # Login to get token
    login_resp = client.post('/api/users/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()['token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = client.put(f'/api/users/{user_id}', json={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'password': 'updatedpass123'
    }, headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'User updated successfully'
    assert 'user' in data
    assert data['user']['username'] == 'updateduser'
    assert data['user']['email'] == 'updated@example.com'
    
    # Verify update
    get_resp = client.get(f'/api/users/{user_id}', headers=headers)
    get_data = get_resp.get_json()
    assert get_data['username'] == 'updateduser'
    assert get_data['email'] == 'updated@example.com'

def test_update_user_invalid_data(client, auth_headers):
    """Test updating user with invalid data."""
    # Register a new user
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    user_id = response.get_json()['user']['id']
    
    # Login to get token
    login_resp = client.post('/api/users/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()['token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = client.put(f'/api/users/{user_id}', json={
        'username': '',
        'email': 'invalid-email',
        'password': '123'
    }, headers=headers)
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'error' in data
    assert 'username' in data['error']
    assert 'email' in data['error']
    assert 'password' in data['error']

def test_update_user_unauthorized(client, auth_headers):
    """Test updating another user's details."""
    # Register user1
    response = client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'pass123'
    })
    assert response.status_code == 201
    user1_id = response.get_json()['user']['id']
    
    # Register user2 and get token
    response = client.post('/api/users/register', json={
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'pass123'
    })
    assert response.status_code == 201
    login_resp = client.post('/api/users/login', json={
        'email': 'user2@example.com',
        'password': 'pass123'
    })
    assert login_resp.status_code == 200
    user2_token = login_resp.get_json()['token']
    user2_headers = {
        'Authorization': f'Bearer {user2_token}',
        'Content-Type': 'application/json'
    }
    
    response = client.put(f'/api/users/{user1_id}', json={
        'username': 'hacked',
        'email': 'hacked@example.com',
        'password': 'hacked123'
    }, headers=user2_headers)
    
    assert response.status_code == 403
    data = response.get_json()
    assert 'error' in data
    assert 'Unauthorized' in data['error']

def test_delete_user(client, auth_headers):
    """Test deleting a user."""
    # Register a new user
    register_resp = client.post('/api/users/register', json={
        'username': 'todelete',
        'email': 'todelete@example.com',
        'password': 'deletepass123'
    })
    assert register_resp.status_code == 201
    user_id = register_resp.get_json()['user']['id']
    
    # Login to get token
    login_resp = client.post('/api/users/login', json={
        'email': 'todelete@example.com',
        'password': 'deletepass123'
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()['token']
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    delete_resp = client.delete(f'/api/users/{user_id}', headers=headers)
    assert delete_resp.status_code == 200
    delete_data = delete_resp.get_json()
    assert 'message' in delete_data
    assert delete_data['message'] == 'User deleted successfully'
    
    # Verify deletion
    get_resp = client.get(f'/api/users/{user_id}', headers=headers)
    assert get_resp.status_code == 404
    
    # Verify login fails
    login_resp = client.post('/api/users/login', json={
        'email': 'todelete@example.com',
        'password': 'deletepass123'
    })
    assert login_resp.status_code == 401

def test_delete_user_unauthorized(client, auth_headers):
    """Test deleting another user's account."""
    # Register user1
    response = client.post('/api/users/register', json={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'pass123'
    })
    assert response.status_code == 201
    user1_id = response.get_json()['user']['id']
    
    # Register user2 and get token
    response = client.post('/api/users/register', json={
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'pass123'
    })
    assert response.status_code == 201
    login_resp = client.post('/api/users/login', json={
        'email': 'user2@example.com',
        'password': 'pass123'
    })
    assert login_resp.status_code == 200
    user2_token = login_resp.get_json()['token']
    user2_headers = {
        'Authorization': f'Bearer {user2_token}',
        'Content-Type': 'application/json'
    }
    
    delete_resp = client.delete(f'/api/users/{user1_id}', headers=user2_headers)
    assert delete_resp.status_code == 403
    data = delete_resp.get_json()
    assert 'error' in data
    assert 'Unauthorized' in data['error']