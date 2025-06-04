import json

def test_create_entry(client, auth_headers):
    """Test creating a journal entry."""
    response = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content',
        'tags': ['test']
    }, headers=auth_headers)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.get_data(as_text=True)}"
    data = response.get_json()
    assert 'id' in data
    assert data['title'] == 'Test Entry'
    assert data['content'] == 'Test content'
    assert data['tags'] == ['test']
    assert '_links' in data
    assert 'self' in data['_links']
    assert data['_links']['self'] == f'/api/entries/{data["id"]}'

def test_create_entry_invalid_data(client, auth_headers):
    """Test creating a journal entry with invalid data."""
    response = client.post('/api/entries', json={
        'title': '',  # Empty title
        'content': 'Test content',
        'tags': ['test']
    }, headers=auth_headers)
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'error' in data
    assert 'title' in data['error']

def test_create_entry_malformed_json(client, auth_headers):
    """Test creating a journal entry with malformed JSON."""
    response = client.post('/api/entries', data='{"title": "Test Entry",}',  # Invalid JSON
                          headers=auth_headers)
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid JSON' in data['error']

def test_get_entries(client, auth_headers):
    """Test retrieving all entries for a user."""
    # Create two entries
    client.post('/api/entries', json={
        'title': 'Entry 1',
        'content': 'Content 1',
        'tags': ['tag1']
    }, headers=auth_headers)
    
    client.post('/api/entries', json={
        'title': 'Entry 2',
        'content': 'Content 2',
        'tags': ['tag2']
    }, headers=auth_headers)
    
    # Get all entries
    response = client.get('/api/entries', headers=auth_headers)
    
    assert response.status_code == 200
    entries = response.get_json()
    assert len(entries) == 2
    titles = [entry['title'] for entry in entries]
    assert 'Entry 1' in titles
    assert 'Entry 2' in titles
    assert all('tags' in entry for entry in entries)
    assert all('_links' in entry for entry in entries)

def test_get_single_entry(client, auth_headers):
    """Test retrieving a single entry."""
    # Create entry
    create_resp = client.post('/api/entries', json={
        'title': 'Single Entry',
        'content': 'Single content',
        'tags': ['single']
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    # Get entry
    get_resp = client.get(f'/api/entries/{entry_id}', headers=auth_headers)
    
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['title'] == 'Single Entry'
    assert data['content'] == 'Single content'
    assert data['tags'] == ['single']
    assert '_links' in data
    assert data['_links']['self'] == f'/api/entries/{entry_id}'

def test_get_single_entry_not_found(client, auth_headers):
    """Test retrieving a non-existent entry."""
    response = client.get('/api/entries/999', headers=auth_headers)
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'Not found' in data['error']

def test_get_single_entry_unauthorized(client, auth_headers):
    """Test retrieving an entry not owned by the user."""
    create_resp = client.post('/api/entries', json={
        'title': 'Single Entry',
        'content': 'Single content',
        'tags': ['single']
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    # Register and login as another user
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    assert login_resp.status_code == 200
    other_token = login_resp.get_json()['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    get_resp = client.get(f'/api/entries/{entry_id}', headers=other_headers)
    
    assert get_resp.status_code == 403
    data = get_resp.get_json()
    assert 'error' in data
    assert 'Not found or unauthorized' in data['error']

def test_update_entry(client, auth_headers):
    """Test updating an entry."""
    create_resp = client.post('/api/entries', json={
        'title': 'Original',
        'content': 'Original content',
        'tags': ['original']
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    update_resp = client.put(f'/api/entries/{entry_id}', json={
        'title': 'Updated',
        'content': 'Updated content',
        'tags': ['updated']
    }, headers=auth_headers)
    
    assert update_resp.status_code == 200
    data = update_resp.get_json()
    assert data['title'] == 'Updated'
    assert data['content'] == 'Updated content'
    assert data['tags'] == ['updated']
    
    # Verify update
    get_resp = client.get(f'/api/entries/{entry_id}', headers=auth_headers)
    data = get_resp.get_json()
    assert data['title'] == 'Updated'
    assert data['content'] == 'Updated content'
    assert data['tags'] == ['updated']

def test_update_entry_invalid_data(client, auth_headers):
    """Test updating an entry with invalid data."""
    create_resp = client.post('/api/entries', json={
        'title': 'Original',
        'content': 'Original content'
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    update_resp = client.put(f'/api/entries/{entry_id}', json={
        'title': '',  # Empty title
        'content': 'Updated content'
    }, headers=auth_headers)
    
    assert update_resp.status_code == 422
    data = update_resp.get_json()
    assert 'error' in data
    assert 'title' in data['error']

def test_update_entry_not_found(client, auth_headers):
    """Test updating a non-existent entry."""
    response = client.put('/api/entries/999', json={
        'title': 'Updated',
        'content': 'Updated content',
        'tags': ['updated']
    }, headers=auth_headers)
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'Not found' in data['error']

def test_update_entry_unauthorized(client, auth_headers):
    """Test updating an entry not owned by the user."""
    create_resp = client.post('/api/entries', json={
        'title': 'Original',
        'content': 'Original content',
        'tags': ['original']
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    # Register and login as another user
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    assert login_resp.status_code == 200
    other_token = login_resp.get_json()['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    update_resp = client.put(f'/api/entries/{entry_id}', json={
        'title': 'Updated',
        'content': 'Updated content',
        'tags': ['updated']
    }, headers=other_headers)
    
    assert update_resp.status_code == 403
    data = update_resp.get_json()
    assert 'error' in data
    assert 'Not found or unauthorized' in data['error']

def test_delete_entry(client, auth_headers):
    """Test deleting an entry."""
    create_resp = client.post('/api/entries', json={
        'title': 'To Delete',
        'content': 'Delete me',
        'tags': ['delete']
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    delete_resp = client.delete(f'/api/entries/{entry_id}', headers=auth_headers)
    
    assert delete_resp.status_code == 200
    data = delete_resp.get_json()
    assert 'message' in data
    assert data['message'] == 'Entry deleted successfully'
    
    # Verify deletion
    get_resp = client.get(f'/api/entries/{entry_id}', headers=auth_headers)
    assert get_resp.status_code == 404  # Changed from 403 to 404, assuming deleted entries are not found

def test_delete_entry_not_found(client, auth_headers):
    """Test deleting a non-existent entry."""
    response = client.delete('/api/entries/999', headers=auth_headers)
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'Not found' in data['error']

def test_delete_entry_unauthorized(client, auth_headers):
    """Test deleting an entry not owned by the user."""
    create_resp = client.post('/api/entries', json={
        'title': 'To Delete',
        'content': 'Delete me',
        'tags': ['delete']
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    entry_id = create_resp.get_json()['id']
    
    # Register and login as another user
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    assert login_resp.status_code == 200
    other_token = login_resp.get_json()['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    delete_resp = client.delete(f'/api/entries/{entry_id}', headers=other_headers)
    
    assert delete_resp.status_code == 403
    data = delete_resp.get_json()
    assert 'error' in data
    assert 'Not found or unauthorized' in data['error']