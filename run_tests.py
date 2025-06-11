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
        "pylint journalapi/",
        "pylint client/",
        "pytest --cov=journalapi tests/",
        "pytest --cov=client tests/",
    ]

    for command in commands:
        return_code = run_command(command)
        if return_code != 0:
            print(f"Command failed: {command}")

    print("All commands completed successfully!")

if __name__ == "__main__":
    main()
