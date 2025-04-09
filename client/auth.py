# PWP_JournalAPI/client/auth.py
def auth_header():
    token = get_token()
    return {"Authorization": f"Bearer {token}"} if token else {}
