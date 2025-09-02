import os
import shutil
import sys

def copy_o_files(source_dir, destination_dir):
    # Walk through the source directory and its subdirectories
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.o'):
                # Construct full file path
                file_path = os.path.join(root, file)
                
                # Compute the relative path from the source directory
                relative_path = os.path.relpath(root, source_dir)
                
                # Create the corresponding directory structure in the destination
                dest_path = os.path.join(destination_dir, relative_path)
                os.makedirs(dest_path, exist_ok=True)
                
                # Copy the file to the destination directory, preserving structure
                shutil.copy(file_path, dest_path)
                print(f"Copied: {file_path} to {dest_path}")

if __name__ == "__main__":
    # Check if the script is called with the right number of arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <destination_directory>")
        sys.exit(1)

    # Get the directory where the script is located
    source_directory = os.path.dirname(os.path.abspath(__file__))
    destination_directory = sys.argv[1]

    copy_o_files(source_directory, destination_directory)