"""Test journal entry endpoints."""
import json

def test_create_entry(client, auth_headers):
    """Test creating a journal entry."""
    response = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content',
        'tags': ['test']
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert '_links' in data

def test_get_entries(client, auth_headers):
    """Test retrieving all entries for a user."""
    # Create two entries
    client.post('/api/entries', json={
        'title': 'Entry 1',
        'content': 'Content 1'
    }, headers=auth_headers)
    
    client.post('/api/entries', json={
        'title': 'Entry 2',
        'content': 'Content 2'
    }, headers=auth_headers)
    
    # Get all entries
    response = client.get('/api/entries', headers=auth_headers)
    
    assert response.status_code == 200
    entries = response.get_json()
    assert len(entries) == 2
    assert entries[0]['title'] in ('Entry 1', 'Entry 2')

def test_get_single_entry(client, auth_headers):
    """Test retrieving a single entry."""
    # Create entry
    create_resp = client.post('/api/entries', json={
        'title': 'Single Entry',
        'content': 'Single content'
    }, headers=auth_headers)
    entry_id = create_resp.get_json()['id']
    
    # Get entry
    get_resp = client.get(f'/api/entries/{entry_id}', headers=auth_headers)
    
    assert get_resp.status_code == 200
    assert get_resp.get_json()['title'] == 'Single Entry'

def test_update_entry(client, auth_headers):
    """Test updating an entry."""
    # Create entry
    create_resp = client.post('/api/entries', json={
        'title': 'Original',
        'content': 'Original content'
    }, headers=auth_headers)
    entry_id = create_resp.get_json()['id']
    
    # Update entry
    update_resp = client.put(f'/api/entries/{entry_id}', json={
        'title': 'Updated',
        'content': 'Updated content',
        'tags': ['updated']
    }, headers=auth_headers)
    
    assert update_resp.status_code == 200
    
    # Verify update
    get_resp = client.get(f'/api/entries/{entry_id}', headers=auth_headers)
    data = get_resp.get_json()
    assert data['title'] == 'Updated'
    assert data['content'] == 'Updated content'
    assert 'updated' in data['tags']

def test_delete_entry(client, auth_headers):
    """Test deleting an entry."""
    # Create entry
    create_resp = client.post('/api/entries', json={
        'title': 'To Delete',
        'content': 'Delete me'
    }, headers=auth_headers)
    entry_id = create_resp.get_json()['id']
    
    # Delete entry
    delete_resp = client.delete(f'/api/entries/{entry_id}', headers=auth_headers)
    
    assert delete_resp.status_code == 200
    
    # Verify deletion
    get_resp = client.get(f'/api/entries/{entry_id}', headers=auth_headers)
    assert get_resp.status_code == 403