"""Test utility functions."""
from journalapi.utils import json_response
from journalapi.models import User
from werkzeug.security import generate_password_hash

def test_json_response():
    """Test the json_response utility function."""
    data = {'key': 'value'}
    response, status, headers = json_response(data, 201)
    
    assert status == 201
    assert headers['Content-Type'] == 'application/json'
    assert 'key' in response

def test_authenticate_user(db):
    """Test user authentication utility."""
    # Create a test user
    user = User(
        username='testauth',
        email='auth@example.com',
        password_hash=generate_password_hash('authpass')
    )
    db.session.add(user)
    db.session.commit()
    
    # Test authentication
    from journalapi.utils import authenticate_user
    authenticated = authenticate_user('testauth', 'authpass')
    assert authenticated is not None
    assert authenticated.username == 'testauth'
    
    # Test failed authentication
    failed = authenticate_user('testauth', 'wrongpass')
    assert failed is None

def test_generate_token():
    """Test token generation utility."""
    from journalapi.utils import generate_token
    from journalapi.models import User
    
    # Create a mock user
    user = User(id=1, username='tokenuser')
    
    token = generate_token(user)
    assert isinstance(token, str)
    assert len(token) > 0