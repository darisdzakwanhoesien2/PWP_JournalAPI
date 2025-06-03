"""Test edit history functionality."""
import json

def test_get_edit_history(client, auth_headers):
    """Test retrieving edit history for a journal entry."""
    # Create entry
    entry_resp = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'Initial content',
        'tags': ['test']
    }, headers=auth_headers)
    entry_id = entry_resp.get_json()['id']
    
    # Make an edit
    client.put(f'/api/entries/{entry_id}', json={
        'title': 'Updated Entry',
        'content': 'Updated content',
        'tags': ['updated']
    }, headers=auth_headers)
    
    # Get edit history
    history_resp = client.get(
        f'/api/entries/{entry_id}/history',
        headers=auth_headers
    )
    
    assert history_resp.status_code == 200
    history = history_resp.get_json()
    assert len(history) == 1
    assert history[0]['old_content'] == 'Initial content'
    assert history[0]['new_content'] == 'Updated content'