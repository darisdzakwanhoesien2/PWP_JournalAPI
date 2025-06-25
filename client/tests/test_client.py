import pytest
from unittest.mock import patch, MagicMock
from client import client

@pytest.fixture
def api_client():
    return client.APIClient()

@patch('client.client.requests.post')
def test_login_success(mock_post, api_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'access_token': 'fake_token'}
    mock_post.return_value = mock_response

    api_client.login('testuser')
    assert api_client.access_token == 'fake_token'

@patch('client.client.requests.post')
def test_login_failure_json(mock_post, api_client):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {'msg': 'Invalid username'}
    mock_post.return_value = mock_response

    with patch('builtins.print') as mock_print:
        api_client.login('baduser')
        mock_print.assert_called_with('Login failed: Invalid username')
    assert api_client.access_token is None

@patch('client.client.requests.post')
def test_login_failure_no_json(mock_post, api_client):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.side_effect = Exception("No JSON")
    mock_post.return_value = mock_response

    with patch('builtins.print') as mock_print:
        api_client.login('baduser')
        mock_print.assert_called_with('Login failed: HTTP 500 error with no JSON response')
    assert api_client.access_token is None

@patch('client.client.requests.get')
def test_get_entries_success(mock_get, api_client):
    api_client.access_token = 'fake_token'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'items': [
            {'id': 1, 'title': 'Entry 1', 'user_id': 1, 'content': 'Content 1'},
            {'id': 2, 'title': 'Entry 2', 'user_id': 2, 'content': 'Content 2'}
        ]
    }
    mock_get.return_value = mock_response

    with patch('builtins.print') as mock_print:
        api_client.get_entries()
        mock_print.assert_any_call('ID: 1, Title: Entry 1, User ID: 1')
        mock_print.assert_any_call('Content: Content 1')
        mock_print.assert_any_call('ID: 2, Title: Entry 2, User ID: 2')
        mock_print.assert_any_call('Content: Content 2')

@patch('client.client.requests.get')
def test_get_entries_no_auth(mock_get, api_client):
    api_client.access_token = None
    with patch('builtins.print') as mock_print:
        api_client.get_entries()
        mock_print.assert_called_with('You must login first.')

@patch('client.client.requests.get')
def test_get_entries_failure(mock_get, api_client):
    api_client.access_token = 'fake_token'
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    with patch('builtins.print') as mock_print:
        api_client.get_entries()
        mock_print.assert_called_with('Failed to get entries: 500')

def test_logout(api_client):
    api_client.access_token = 'fake_token'
    with patch('builtins.print') as mock_print:
        api_client.logout()
        mock_print.assert_called_with('Logged out.')
    assert api_client.access_token is None
