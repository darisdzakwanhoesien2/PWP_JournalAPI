from pathlib import Path

def export_code_and_directory_list(root_directory=".", code_file="code.txt", list_file="directories.txt"):
    root = Path(root_directory)
    # Get all Python files recursively under the root_directory
    python_files = list(root.rglob("*.py"))
    
    # Open both output files for writing
    with open(code_file, "w", encoding="utf-8") as code_out, open(list_file, "w", encoding="utf-8") as list_out:
        for file_path in python_files:
            # Write just the path in the directory list file
            list_out.write(f"{file_path}\n")
            
            # For the code file, include a header with the file path, then the file's contents
            code_out.write(f"# {file_path}\n")
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                content = f"# Error reading {file_path}: {e}"
            code_out.write(content)
            code_out.write("\n\n")  # Separate individual files with newlines

if __name__ == "__main__":
    # Adjust the 'root_directory' if your repository root is different
    export_code_and_directory_list(root_directory=".", code_file="code.txt", list_file="directories.txt")
