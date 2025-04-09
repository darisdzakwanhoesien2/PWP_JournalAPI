import os

def write_python_files_to_txt(root_directory=".", output_file="output.txt"):
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Walk through the root directory and all subdirectories
        for dirpath, dirnames, filenames in os.walk(root_directory):
            for filename in filenames:
                if filename.endswith(".py"):
                    # Construct the full file path
                    file_path = os.path.join(dirpath, filename)
                    # Write the file path to the output file as a comment header
                    outfile.write(f"# {file_path}\n")
                    try:
                        # Read the file content
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                        outfile.write(content)
                    except Exception as e:
                        # In case of any errors, write an error message
                        outfile.write(f"# Error reading {file_path}: {e}\n")
                    # Add a couple of newlines as a separator between files
                    outfile.write("\n\n")

if __name__ == "__main__":
    # Adjust the root directory if your repo is elsewhere
    write_python_files_to_txt(root_directory=".", output_file="output.txt")
