import json

def test_get_edit_history(client, auth_headers):
    """Test retrieving edit history for a journal entry."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Initial content',
        'tags': ['test']
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    client.put(f'/api/entries/{entry_id}', json={
        'title': 'Updated Entry',
        'content': 'Updated content',
        'tags': ['updated']
    }, headers=auth_headers)
    
    history_resp = client.get(
        f'/api/entries/{entry_id}/history',
        headers=auth_headers
    )
    
    assert history_resp.status_code == 200
    history = history_resp.get_json()
    assert len(history) == 1
    assert history[0]['old_content'] == 'Initial content'
    assert history[0]['new_content'] == 'Updated content'

def test_get_edit_history_unauthorized(client, auth_headers):
    """Test retrieving edit history for a journal entry not owned by the user."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Initial content',
        'tags': ['test']
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass123'
    })
    other_token = login_resp.get_json()['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    history_resp = client.get(
        f'/api/entries/{entry_id}/history',
        headers=other_headers
    )
    
    assert history_resp.status_code == 403
    assert 'Journal entry not found or unauthorized' in history_resp.get_json()['error']