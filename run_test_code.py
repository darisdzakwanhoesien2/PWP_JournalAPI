import subprocess

def run_command(command):
    """Runs a command and prints the output."""
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode())
    if stderr:
        print(f"Error:\n{stderr.decode()}")
    return process.returncode

def main():
    """Runs the pylint and pytest commands."""
    commands = [
        "python init_db.py",
        "python insert_from_files.py",
        # "flask --app app run --port=8000",
        "cd client/ && python main.py auth register --username alice --email alice@example.com --password secure123",
        "cd client/ && python main.py auth login --email alice@example.com --password secure123",
        "cd client/ && python main.py entry list",
        "cd client/ && python main.py entry create --title \"Test\" --content \"My first entry\" --tags life,personal",
        # "pytest --cov=journalapi tests/",
    ]

    for command in commands:
        return_code = run_command(command)
        if return_code != 0:
            print(f"Command failed: {command}")

    print("All commands completed successfully!")

if __name__ == "__main__":
    main()
