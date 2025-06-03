"""Test comment-related endpoints."""
import json
import pytest
from journalapi.models import JournalEntry, Comment
from extensions import db

def test_add_comment(client, auth_headers):
    """Test adding a comment to a journal entry."""
    # Create a journal entry
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content',
        'tags': ['test']
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    # Add comment
    comment_data = {'content': 'Test comment'}
    response = client.post(
        f'/api/entries/{entry_id}/comments',
        json=comment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert 'id' in response.get_json()
    
    # Verify comment exists
    get_response = client.get(
        f'/api/entries/{entry_id}/comments',
        headers=auth_headers
    )
    assert get_response.status_code == 200
    comments = get_response.get_json()
    assert len(comments) == 1
    assert comments[0]['content'] == 'Test comment'

def test_add_comment_invalid_entry(client, auth_headers):
    """Test adding a comment to a non-existent journal entry (covers lines 38-41)."""
    response = client.post(
        '/api/entries/999/comments',
        json={'content': 'Test comment'},
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Entry not found' in response.get_json()['error']

def test_add_comment_invalid_data(client, auth_headers, app):
    """Test adding a comment with invalid data (covers lines 47-49)."""
    # Create a journal entry
    with app.app_context():
        user_id = 1  # Assumes user_id from auth_headers
        entry = JournalEntry(user_id=user_id, title='Test Entry', content='Test content', tags='[]')
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id
    
    # Attempt to add comment with empty content (violates CommentSchema)
    response = client.post(
        f'/api/entries/{entry_id}/comments',
        json={'content': ''},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    assert 'content' in response.get_json()['error']
    assert 'Shorter than minimum length 1' in str(response.get_json()['error'])

def test_get_comments_invalid_entry(client, auth_headers):
    """Test retrieving comments for a non-existent journal entry (covers lines 24-27)."""
    response = client.get(
        '/api/entries/999/comments',
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Entry not found' in response.get_json()['error']

def test_get_single_comment_not_found(client, auth_headers):
    """Test retrieving a non-existent comment (covers lines 63-66)."""
    # Create a journal entry
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Test content'
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    # Attempt to get a non-existent comment
    response = client.get(
        f'/api/entries/{entry_id}/comments/999',
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert 'Not found' in response.get_json()['error']

def test_update_comment(client, auth_headers):
    """Test updating a comment."""
    # Create entry and comment
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
    
    # Update comment
    update_resp = client.put(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        json={'content': 'Updated comment'},
        headers=auth_headers
    )
    
    assert update_resp.status_code == 200
    
    # Verify update
    get_resp = client.get(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=auth_headers
    )
    assert get_resp.get_json()['content'] == 'Updated comment'

def test_update_comment_unauthorized(client, auth_headers, app):
    """Test updating a comment not owned by the user (covers lines 77-80)."""
    # Create a journal entry and comment as user 1
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
    
    # Create a second user
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    other_token = json.loads(login_resp.get_data(as_text=True))['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    # Attempt to update comment as second user
    response = client.put(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        json={'content': 'Unauthorized update'},
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert 'Not found or unauthorized' in response.get_json()['error']

def test_update_comment_invalid_data(client, auth_headers):
    """Test updating a comment with invalid data (covers lines 87-89)."""
    # Create entry and comment
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
    
    # Attempt to update with empty content (violates CommentSchema)
    response = client.put(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        json={'content': ''},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    assert 'content' in response.get_json()['error']
    assert 'Shorter than minimum length 1' in str(response.get_json()['error'])

def test_delete_comment(client, auth_headers):
    """Test deleting a comment."""
    # Create entry and comment
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
    
    # Delete comment
    delete_resp = client.delete(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=auth_headers
    )
    
    assert delete_resp.status_code == 200
    
    # Verify deletion
    get_resp = client.get(
        f'/api/entries/{entry_id}/comments',
        headers=auth_headers
    )
    assert len(get_resp.get_json()) == 0

def test_delete_comment_unauthorized(client, auth_headers):
    """Test deleting a comment not owned by the user (covers lines 99-102)."""
    # Create a journal entry and comment as user 1
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
    
    # Create a second user
    client.post('/api/users/register', json={
        'username': 'otheruser',
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    login_resp = client.post('/api/users/login', json={
        'email': 'other@example.com',
        'password': 'otherpass'
    })
    other_token = json.loads(login_resp.get_data(as_text=True))['token']
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    # Attempt to delete comment as second user
    response = client.delete(
        f'/api/entries/{entry_id}/comments/{comment_id}',
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert 'Not found or unauthorized' in response.get_json()['error']