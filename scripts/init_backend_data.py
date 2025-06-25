import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def init_users():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if os.path.exists(USERS_FILE):
        print(f"{USERS_FILE} already exists. Skipping initialization.")
        return
    users = [
        {
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com"
        }
    ]
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)
    print(f"Initialized users data with testuser in {USERS_FILE}")

if __name__ == "__main__":
    init_users()
