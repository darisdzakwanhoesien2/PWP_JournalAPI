import requests
from datetime import datetime

API_BASE_URL = "http://localhost:5000"

class APIClient:
    def __init__(self):
        self.access_token = None
        self.current_user = None

    def login(self, username):
        """Log in to the API and store the JWT token."""
        url = f"{API_BASE_URL}/login"
        try:
            response = requests.post(url, json={"username": username})
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                self.current_user = username
                print(f"Successfully logged in as {username}")
                return True
            else:
                try:
                    error_msg = response.json().get('msg', 'Unknown error')
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Login failed: {error_msg}")
                return False
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            return False

    def register(self, username, email, password):
        """Register a new user."""
        url = f"{API_BASE_URL}/users/register"
        data = {"username": username, "email": email, "password": password}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                print(f"User {username} registered successfully!")
                return True
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Registration failed: {error_msg}")
                return False
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            return False

    def get_entries(self):
        """Retrieve and display all entries."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/entries"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                entries = data.get("items", [])
                if not entries:
                    print("No entries found.")
                else:
                    print("\nJournal Entries:")
                    print("-" * 50)
                    for entry in entries:
                        print(f"ID: {entry['id']}")
                        print(f"Title: {entry['title']}")
                        print(f"Content: {entry['content']}")
                        print(f"User ID: {entry['user_id']}")
                        print(f"Created: {entry['created_at']}")
                        print(f"Updated: {entry['updated_at']}")
                        print(f"Links: {entry['_links']}")
                        print("-" * 50)
            else:
                print(f"Failed to get entries: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def create_entry(self, user_id, title, content):
        """Create a new journal entry."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/entries"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"user_id": user_id, "title": title, "content": content}
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                entry = response.json()
                print("\nEntry created successfully:")
                print(f"ID: {entry['id']}")
                print(f"Title: {entry['title']}")
                print(f"Content: {entry['content']}")
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Failed to create entry: {error_msg}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def update_entry(self, entry_id, title=None, content=None):
        """Update an existing journal entry."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/entries/{entry_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if not data:
            print("No update data provided.")
            return
        try:
            response = requests.put(url, json=data, headers=headers)
            if response.status_code == 200:
                entry = response.json()
                print("\nEntry updated successfully:")
                print(f"ID: {entry['id']}")
                print(f"Title: {entry['title']}")
                print(f"Content: {entry['content']}")
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Failed to update entry: {error_msg}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def delete_entry(self, entry_id):
        """Delete a journal entry."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/entries/{entry_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 204:
                print(f"Entry {entry_id} deleted successfully.")
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Failed to delete entry: {error_msg}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def get_comments(self, entry_id):
        """Retrieve and display comments for an entry."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/entries/{entry_id}/comments"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                comments = data.get("items", [])
                if not comments:
                    print(f"No comments found for entry {entry_id}.")
                else:
                    print(f"\nComments for Entry {entry_id}:")
                    print("-" * 50)
                    for comment in comments:
                        print(f"Comment ID: {comment['id']}")
                        print(f"Content: {comment['content']}")
                        print(f"User ID: {comment['user_id']}")
                        print(f"Created: {comment['created_at']}")
                        print(f"Updated: {comment['updated_at']}")
                        print(f"Links: {comment['_links']}")
                        print("-" * 50)
            else:
                print(f"Failed to get comments: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def add_comment(self, entry_id, user_id, content):
        """Add a comment to an entry."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/entries/{entry_id}/comments"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"user_id": user_id, "content": content}
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                comment = response.json()
                print("\nComment added successfully:")
                print(f"Comment ID: {comment['id']}")
                print(f"Content: {comment['content']}")
                print(f"Entry ID: {comment['entry_id']}")
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Failed to add comment: {error_msg}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def update_comment(self, comment_id, content):
        """Update an existing comment."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/comments/{comment_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"content": content}
        try:
            response = requests.put(url, json=data, headers=headers)
            if response.status_code == 200:
                comment = response.json()
                print("\nComment updated successfully:")
                print(f"Comment ID: {comment['id']}")
                print(f"Content: {comment['content']}")
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Failed to update comment: {error_msg}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def delete_comment(self, comment_id):
        """Delete a comment."""
        if not self._check_auth():
            return
        url = f"{API_BASE_URL}/comments/{comment_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 204:
                print(f"Comment {comment_id} deleted successfully.")
            else:
                try:
                    error_msg = response.json()
                except Exception:
                    error_msg = f"HTTP {response.status_code} error with no JSON response"
                print(f"Failed to delete comment: {error_msg}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

    def logout(self):
        """Log out and clear the JWT token."""
        if self.access_token:
            self.access_token = None
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Not logged in.")

    def _check_auth(self):
        """Check if the client is authenticated."""
        if not self.access_token:
            print("You must log in first.")
            return False
        return True

def display_menu():
    """Display the main menu."""
    print("\n=== Journal API Client ===")
    print("1. Register")
    print("2. Login")
    print("3. View All Entries")
    print("4. Create Entry")
    print("5. Update Entry")
    print("6. Delete Entry")
    print("7. View Comments for an Entry")
    print("8. Add Comment")
    print("9. Update Comment")
    print("10. Delete Comment")
    print("11. Logout")
    print("12. Exit")
    print("========================")

def main():
    client = APIClient()
    while True:
        display_menu()
        choice = input("Select an option (1-12): ").strip()
        
        if choice == "1":
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            if username and email and password:
                client.register(username, email, password)
            else:
                print("All fields are required for registration.")
        
        elif choice == "2":
            username = input("Enter username: ").strip()
            if username:
                client.login(username)
            else:
                print("Username is required.")
        
        elif choice == "3":
            client.get_entries()
        
        elif choice == "4":
            try:
                user_id = int(input("Enter user ID: ").strip())
                title = input("Enter entry title: ").strip()
                content = input("Enter entry content: ").strip()
                if user_id and title and content:
                    client.create_entry(user_id, title, content)
                else:
                    print("All fields are required.")
            except ValueError:
                print("User ID must be an integer.")
        
        elif choice == "5":
            try:
                entry_id = int(input("Enter entry ID: ").strip())
                title = input("Enter new title (or press Enter to skip): ").strip()
                content = input("Enter new content (or press Enter to skip): ").strip()
                if entry_id:
                    client.update_entry(entry_id, title or None, content or None)
                else:
                    print("Entry ID is required.")
            except ValueError:
                print("Entry ID must be an integer.")
        
        elif choice == "6":
            try:
                entry_id = int(input("Enter entry ID to delete: ").strip())
                if entry_id:
                    client.delete_entry(entry_id)
                else:
                    print("Entry ID is required.")
            except ValueError:
                print("Entry ID must be an integer.")
        
        elif choice == "7":
            try:
                entry_id = int(input("Enter entry ID: ").strip())
                if entry_id:
                    client.get_comments(entry_id)
                else:
                    print("Entry ID is required.")
            except ValueError:
                print("Entry ID must be an integer.")
        
        elif choice == "8":
            try:
                entry_id = int(input("Enter entry ID: ").strip())
                user_id = int(input("Enter user ID: ").strip())
                content = input("Enter comment content: ").strip()
                if entry_id and user_id and content:
                    client.add_comment(entry_id, user_id, content)
                else:
                    print("All fields are required.")
            except ValueError:
                print("Entry ID and user ID must be integers.")
        
        elif choice == "9":
            try:
                comment_id = int(input("Enter comment ID: ").strip())
                content = input("Enter new comment content: ").strip()
                if comment_id and content:
                    client.update_comment(comment_id, content)
                else:
                    print("Comment ID and content are required.")
            except ValueError:
                print("Comment ID must be an integer.")
        
        elif choice == "10":
            try:
                comment_id = int(input("Enter comment ID to delete: ").strip())
                if comment_id:
                    client.delete_comment(comment_id)
                else:
                    print("Comment ID is required.")
            except ValueError:
                print("Comment ID must be an integer.")
        
        elif choice == "11":
            client.logout()
        
        elif choice == "12":
            print("Exiting client.")
            break
        else:
            print("Invalid option. Please select 1-12.")

if __name__ == "__main__":
    main()