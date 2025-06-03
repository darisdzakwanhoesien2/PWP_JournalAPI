from pathlib import Path
import json

def extract_content_from_ipynb(file_path: Path) -> str:
    """
    Extracts and concatenates the content of a Jupyter Notebook (.ipynb) file.
    Both code cells and markdown cells are extracted, preserving the order.
    Each cell is annotated with a header indicating its type.
    """
    try:
        notebook = json.loads(file_path.read_text(encoding="utf-8"))
        cells = notebook.get("cells", [])
        content_lines = []
        for idx, cell in enumerate(cells, start=1):
            cell_type = cell.get("cell_type", "unknown")
            # Add a header for this cell
            if cell_type == "code":
                content_lines.append(f"### Cell {idx}: Code")
            elif cell_type == "markdown":
                content_lines.append(f"### Cell {idx}: Markdown")
            else:
                content_lines.append(f"### Cell {idx}: {cell_type}")
            # Join the source lines; they are typically stored as a list of lines.
            source = "".join(cell.get("source", []))
            content_lines.append(source)
            content_lines.append("\n")  # Extra newline after each cell
        return "\n".join(content_lines)
    except Exception as e:
        return f"# Error reading {file_path}: {e}"

def export_code_and_directory_list(root_directory=".", code_file="code.txt", list_file="directories.txt"):
    """
    Traverses the given root directory to find all files with a .py or .ipynb extension.
    Writes to two files:
      - directories.txt: A list of the file paths.
      - code.txt: Each file’s path (as header) followed by its content.
        For .ipynb files, both code and markdown cells are included.
    """
    root = Path(root_directory)
    # Collect both .py and .ipynb files
    files = list(root.rglob("*.py")) + list(root.rglob("*.ipynb"))
    # Optional: sort files for a consistent order
    files.sort(key=lambda p: p.as_posix())

    with open(code_file, "w", encoding="utf-8") as code_out, open(list_file, "w", encoding="utf-8") as list_out:
        for file_path in files:
            # Write the file path to the directories file
            list_out.write(f"{file_path}\n")
            
            # Write the file path header in the code file
            code_out.write(f"# {file_path}\n")
            
            # Process the file according to its extension
            if file_path.suffix == ".ipynb":
                content = extract_content_from_ipynb(file_path)
            else:
                try:
                    content = file_path.read_text(encoding="utf-8")
                except Exception as e:
                    content = f"# Error reading {file_path}: {e}"
            
            code_out.write(content)
            code_out.write("\n\n")  # Add separation for readability

if __name__ == "__main__":
    # Adjust 'root_directory' if your repository root is different.
    export_code_and_directory_list(root_directory=".", code_file="code.txt", list_file="directories.txt")
