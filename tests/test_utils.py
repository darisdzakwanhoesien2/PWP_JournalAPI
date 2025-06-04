import pytest
import json
from flask import current_app
from journalapi.utils import json_response, authenticate_user, generate_token, handle_error
from journalapi.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from pytest_mock import MockerFixture

def test_json_response():
    """Test the json_response utility function."""
    data = {'key': 'value'}
    response = json_response(data, 201)
    
    assert response.status_code == 201
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True)) == data
    assert response.headers['Content-Type'] == 'application/json'

def test_json_response_non_serializable():
    """Test json_response with non-serializable data."""
    data = {'key': set([1, 2, 3])}  # Sets are not JSON serializable
    with pytest.raises(TypeError, match="is not JSON serializable"):
        json_response(data, 200)

def test_json_response_different_status():
    """Test json_response with different status code."""
    data = {'message': 'OK'}
    response = json_response(data, 404)
    
    assert response.status_code == 404
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True)) == data

def test_authenticate_user(app, db):
    """Test user authentication utility."""
    with app.app_context():
        user = User(
            username='testauth',
            email='auth@example.com',
            password_hash=generate_password_hash('authpass')
        )
        db.session.add(user)
        db.session.commit()
        
        authenticated = authenticate_user('testauth', 'authpass')
        assert authenticated is not None
        assert authenticated.username == 'testauth'
        assert authenticated.email == 'auth@example.com'
        assert check_password_hash(authenticated.password_hash, 'authpass')
        
        failed = authenticate_user('testauth', 'wrongpass')
        assert failed is None

def test_authenticate_user_non_existent(app, db):
    """Test authentication with non-existent user."""
    with app.app_context():
        authenticated = authenticate_user('nonexistent', 'anypass')
        assert authenticated is None

def test_authenticate_user_empty_credentials(app, db):
    """Test authentication with empty credentials."""
    with app.app_context():
        with pytest.raises(ValueError, match="Username and password are required"):
            authenticate_user('', '')
        with pytest.raises(ValueError, match="Username and password are required"):
            authenticate_user('testauth', '')
        with pytest.raises(ValueError, match="Username and password are required"):
            authenticate_user('', 'anypass')

def test_generate_token(app, mocker: MockerFixture):
    """Test token generation utility."""
    with app.app_context():
        user = User(id=1, username='tokenuser')
        mock_jwt = mocker.patch("journalapi.utils.jwt.encode")
        mock_jwt.return_value = "mocked_token"
        
        token = generate_token(user)
        
        assert token == 'mocked_token'
        mock_jwt.assert_called_once()
        call_args = mock_jwt.call_args[0]
        payload = call_args[0]
        assert payload['user_id'] == 1
        assert payload['username'] == 'tokenuser'
        assert 'exp' in payload
        assert call_args[1] == current_app.config['SECRET_KEY']
        assert call_args[2] == 'HS256'

def test_generate_token_invalid_user(app, mocker: MockerFixture):
    """Test token generation with invalid user."""
    with app.app_context():
        user = User(id=None, username='invaliduser')  # Missing ID
        with pytest.raises(ValueError, match="User must have a valid ID"):
            generate_token(user)

def test_generate_token_missing_config(app, mocker: MockerFixture):
    """Test token generation with missing secret key."""
    with app.app_context():
        user = User(id=1, username='tokenuser')
        mocker.patch.dict(current_app.config, {'SECRET_KEY': None})
        with pytest.raises(ValueError, match="Missing JWT secret key"):
            generate_token(user)

def test_handle_error(app, mocker: MockerFixture):
    """Test handle_error utility with JSON response."""
    with app.app_context():
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"error": "Bad request"}
        mock_response.text = "Bad request"
        mock_response.status_code = 400
        mock_logger = mocker.patch("journalapi.utils.logger.error")
        
        result = handle_error(mock_response, Exception("test"), "Test error")
        
        assert result == {"error": "Bad request"}
        mock_logger.error.assert_called_with("Test error: %s", {"error": "Bad request"})

def test_handle_error_no_json(app, mocker: MockerFixture):
    """Test handle_error with no JSON response."""
    with app.app_context():
        mock_response = mocker.Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Server error"
        mock_response.status_code = 500
        mock_logger = mocker.patch("journalapi.utils.logger.error")
        
        result = handle_error(mock_response, Exception("test"), "Test error")
        
        assert result == {"error": "Server error"}
        mock_logger.error.assert_called_with("Test error: %s", "Server error")