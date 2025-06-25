import requests

API_BASE_URL = "http://localhost:5000"

class APIClient:
    def __init__(self):
        self.access_token = None

    def login(self, username):
        url = f"{API_BASE_URL}/login"
        response = requests.post(url, json={"username": username})
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            print(f"Logged in as {username}")
        else:
            try:
                error_msg = response.json().get('msg', 'Unknown error')
            except Exception:
                error_msg = f"HTTP {response.status_code} error with no JSON response"
            print(f"Login failed: {error_msg}")

    def get_entries(self):
        if not self.access_token:
            print("You must login first.")
            return
        url = f"{API_BASE_URL}/entries"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            entries = response.json().get("items", [])
            if not entries:
                print("No entries found.")
            else:
                for entry in entries:
                    print(f"ID: {entry['id']}, Title: {entry['title']}, User ID: {entry['user_id']}")
                    print(f"Content: {entry['content']}")
                    print("-" * 40)
        else:
            print(f"Failed to get entries: {response.status_code}")

    def logout(self):
        self.access_token = None
        print("Logged out.")

def main():
    client = APIClient()
    while True:
        print("\nCommands: login, entries, logout, exit")
        cmd = input("Enter command: ").strip().lower()
        if cmd == "login":
            username = input("Username: ").strip()
            client.login(username)
        elif cmd == "entries":
            client.get_entries()
        elif cmd == "logout":
            client.logout()
        elif cmd == "exit":
            print("Exiting client.")
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
