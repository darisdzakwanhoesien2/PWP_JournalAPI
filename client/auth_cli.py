# PWP_JournalAPI/client/auth_cli.py
import typer
import requests
from rich import print
import auth, config  # from client

auth_app = typer.Typer(help="Authentication commands")

@auth_app.command("register")
def register(
    username: str = typer.Option(..., "--username", "-u", help="Your desired username"),
    email: str = typer.Option(..., "--email", "-e", help="Your email address"),
    password: str = typer.Option(..., "--password", "-p", hide_input=True, help="Your password")
):
    """
    Register a new user with username, email, and password.
    Handles validation and server errors cleanly.
    """
    res = requests.post(f"{config.API_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    if res.status_code == 201:
        print("[green]✅ Registered![/green]")
    else:
        try:
            err = res.json()
            if "errors" in err:
                print(f"[red]❌ Validation Error: {err['errors']}[/red]")
            elif "error" in err:
                print(f"[red]❌ {err['error']}[/red]")
            else:
                print(f"[red]❌ Unexpected response: {err}[/red]")
        except Exception:
            print(f"[red]❌ Server error: {res.text}[/red]")


@auth_app.command("login")
def login(
    email: str = typer.Option(..., "--email", "-e", help="Your email"),
    password: str = typer.Option(..., "--password", "-p", hide_input=True, help="Your password")
):
    """
    Log in and store the JWT token.
    """
    res = requests.post(f"{config.API_URL}/users/login", json={"email": email, "password": password})
    if res.ok:
        auth.save_token(res.json()["token"])
        print("[green]✅ Logged in[/green]")
    else:
        try:
            err = res.json()
            print(f"[red]❌ Login failed: {err.get('error', err)}[/red]")
        except Exception:
            print(f"[red]❌ Server error: {res.text}[/red]")


@auth_app.command("logout")
def logout():
    """
    Remove saved token (logout).
    """
    auth.clear_token()
    print("[yellow]🔓 Logged out[/yellow]")


@auth_app.command("me")
def me():
    """
    Check if you're logged in.
    """
    token = auth.get_token()
    print("[green]🔐 Logged in[/green]" if token else "[red]🔓 Not logged in[/red]")
