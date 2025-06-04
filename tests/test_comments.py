import json
import pytest
from journalapi.models import JournalEntry, Comment
from extensions import db

def test_add_comment(client, auth_headers):
    """Test adding a comment to a journal entry."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content',
        'tags': ['test']
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    comment_data = {'content': 'Test comment'}
    response = client.post(
        f'/api/entries/{entry_id}/comments',
        json=comment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert 'id' in response.get_json()
    
    get_response = client.get(
        f'/api/entries/{entry_id}/comments',
        headers=auth_headers
    )
    assert get_response.status_code == 200
    comments = get_response.get_json()
    assert len(comments) == 1
    assert comments[0]['content'] == 'Test comment'

def test_add_comment_invalid_entry(client, auth_headers):
    """Test adding a comment to a non-existent journal entry."""
    response = client.post(
        '/api/entries/999/comments',
        json={'content': 'Test comment'},
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Entry not found' in response.get_json()['error']

def test_add_comment_invalid_data(client, auth_headers, app):
    """Test adding a comment with invalid data."""
    with app.app_context():
        user_id = 1
        entry = JournalEntry(user_id=user_id, title='Test Entry', content='Test content', tags='[]')
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id
    
    response = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': ''},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    assert 'content' in response.get_json()['error']

def test_get_comments_invalid_entry(client, auth_headers):
    """Test retrieving comments for a non-existent journal entry."""
    response = client.get(
        '/api/entries/999/comments',
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Entry not found' in response.get_json()['error']

def test_get_single_comment_not_found(client, auth_headers):
    """Test retrieving a non-existent comment."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    response = client.get(
        f'/api/entries/{entry_id}/comments/999',
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Not found' in response.get_json()['error']

def test_get_single_comment_wrong_entry(client, auth_headers):
    """Test retrieving a comment with mismatched entry_id."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    entry_resp2 = client.post('/api/entries', json={
        'title': 'Another Entry',
        'content': 'Another content'
    }, headers=auth_headers)
    entry_id2 = entry_resp2.get_json()['id']
    
    comment_resp = client.post(
        f'/api/entries/{entry_id2}/comments',
        json={'content': 'Test comment'},
        headers=auth_headers
    )
    comment_id = comment_resp.get_json()['id']
    
    response = client.get(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Not found' in response.get_json()['error']

def test_update_comment(client, auth_headers):
    """Test updating a comment."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    comment_resp = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': 'Original comment'},
        headers=auth_headers
    )
    comment_id = comment_resp.get_json()['id']
    
    update_resp = client.put(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        json={'content': 'Updated comment'},
        headers=auth_headers
    )
    
    assert update_resp.status_code == 200
    
    get_resp = client.get(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=auth_headers
    )
    assert get_resp.get_json()['content'] == 'Updated comment'

def test_update_comment_unauthorized(client, auth_headers, app):
    """Test updating a comment not owned by the user."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    comment_resp = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': 'Original comment'},
        headers=auth_headers
    )
    comment_id = comment_resp.get_json()['id']
    
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    other_token = login_resp.get_json()['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    response = client.put(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        json={'content': 'Unauthorized update'},
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert 'Not found or unauthorized' in response.get_json()['error']

def test_update_comment_invalid_data(client, auth_headers):
    """Test updating a comment with invalid data."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    comment_resp = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': 'Original comment'},
        headers=auth_headers
    )
    comment_id = comment_resp.get_json()['id']
    
    response = client.put(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        json={'content': ''},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    assert 'content' in response.get_json()['error']

def test_delete_comment(client, auth_headers):
    """Test deleting a comment."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    comment_resp = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': 'To be deleted'},
        headers=auth_headers
    )
    comment_id = comment_resp.get_json()['id']
    
    delete_resp = client.delete(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=auth_headers
    )
    
    assert delete_resp.status_code == 200
    
    get_resp = client.get(
        f'/api/entries/{entry_id}/comments',
        headers=auth_headers
    )
    assert len(get_resp.get_json()) == 0

def test_delete_comment_unauthorized(client, auth_headers):
    """Test deleting a comment not owned by the user."""
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    comment_resp = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': 'To be deleted'},
        headers=auth_headers
    )
    comment_id = comment_resp.get_json()['id']
    
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    other_token = login_resp.get_json()['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    response = client.delete(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert 'Not found or unauthorized' in response.get_json()['error']