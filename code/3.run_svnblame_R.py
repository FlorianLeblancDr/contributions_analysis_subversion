#author: Florian Leblanc
#purpose: Script to launch svn blame on one folder

import os
import subprocess
import sys

# prior I did manually
# svn checkout --ignore-externals file:///data/repositories/svnroot/Imaclim/ImaclimRWorld/trunk_v2.0/

# Configuration

revision = sys.argv[1]
folder_to_search = sys.argv[2] #'trunk_v2.0/'      # Replace with the folder to start the recursive search

# TODO
# exclude externals

extension_list = ['.c', '.gms', '.sci', '.py', '.R','.sh', '.sce']   # List of file extensions to include

#-----------------------------------------------------------------------------------------------------
# Function to execute a shell command and catch the shell output inside python
def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True, encoding="cp437")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return None
#-----------------------------------------------------------------------------------------------------
# Function to run svn blame on a file
def run_svn_blame(file_path):
    command = ["svn", "blame", file_path]
    svn_blame_output = run_command(command)
    return svn_blame_output
#-----------------------------------------------------------------------------------------------------
# Function to process files with specified extensions recursively
def process_files_recursively(folder):
    result = ''
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            _, file_extension = os.path.splitext(file_path)

            # Check if the file extension is in the extension list
            if file_extension in extension_list:
                print(f"Processing: {file_path}")
                svn_blame_output = run_svn_blame(file_path)
                if svn_blame_output:
                    # Process svn blame output as needed
                    print(svn_blame_output)
                    result += svn_blame_output
    return result
#-----------------------------------------------------------------------------------------------------

# Call the function to process files with specified extensions recursively
result = process_files_recursively(folder_to_search)

#open text file
text_file = open("outputs/svnblame_imaclim_r"+revision+".txt", "w")
#write string to file
text_file.write(result)
#close file
text_file.close()
