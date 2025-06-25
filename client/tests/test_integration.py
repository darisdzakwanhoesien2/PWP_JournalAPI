import subprocess
import sys
import time
import pytest

API_BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module", autouse=True)
def check_backend_running():
    import requests
    try:
        r = requests.get(f"{API_BASE_URL}/entries")
        assert r.status_code in (200, 401, 403)  # 401/403 if no auth, 200 if public
    except Exception as e:
        pytest.skip(f"Backend API not running at {API_BASE_URL}: {e}")

def run_client_command(commands):
    """
    Run the client.py script with a sequence of commands.
    commands: list of strings to send as input lines.
    Returns stdout and stderr as strings.
    """
    proc = subprocess.Popen(
        [sys.executable, "client/client.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    input_str = "\n".join(commands) + "\n"
    try:
        stdout, stderr = proc.communicate(input=input_str, timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    return stdout, stderr

import requests

def register_test_user():
    url = "http://localhost:5000/users/register"
    data = {
        "username": "testuser",
        "email": "testuser@example.com"
    }
    try:
        response = requests.post(url, json=data)
        # It's okay if user already exists
        if response.status_code not in (200, 201, 400):
            pytest.skip(f"Failed to register test user: {response.status_code} {response.text}")
    except Exception as e:
        pytest.skip(f"Exception during user registration: {e}")

def test_login_and_get_entries():
    register_test_user()
    # Test login, get entries, logout, exit
    commands = [
        "login",
        "testuser",
        "entries",
        "logout",
        "exit"
    ]
    stdout, stderr = run_client_command(commands)
    assert "Logged in as testuser" in stdout
    assert "ID:" in stdout or "No entries found." in stdout
    assert "Logged out." in stdout
    assert stderr == ""

def test_login_invalid_user():
    commands = [
        "login",
        "",  # empty username
        "exit"
    ]
    stdout, stderr = run_client_command(commands)
    assert ("Login failed" in stdout or "Missing username" in stdout or "Logged in as" not in stdout)
    assert stderr == ""
