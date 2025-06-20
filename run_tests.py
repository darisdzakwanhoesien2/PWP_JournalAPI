import subprocess
import sys

def run_pytest():
    print("Running pytest...")
    result = subprocess.run([sys.executable, "-m", "pytest", "--maxfail=1", "--disable-warnings", "-q"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Pytest failed.")
    else:
        print("Pytest passed successfully.")

def run_pylint():
    print("Running pylint on src/ directory...")
    result = subprocess.run([sys.executable, "-m", "pylint", "src/"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Pylint found issues.")
    else:
        print("Pylint passed successfully.")

if __name__ == "__main__":
    run_pytest()
    print("\n" + "="*80 + "\n")
    run_pylint()
