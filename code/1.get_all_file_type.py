#author: Florian Leblanc
#purpose: Script to list all file type of a given checkout

import os

# Function to list all file types in a directory recursively
def list_file_types(directory):
    file_types = set()  # Use a set to store unique file types

    for root, _, files in os.walk(directory):
        for file in files:
            # Split the file name into its base name and extension
            base_name, extension = os.path.splitext(file)
            if extension:
                # Add the extension (without the dot) to the set
                file_types.add(extension[1:])  # [1:] removes the dot from the extension

    return list(file_types)

# Specify the directory you want to search in
directory_to_search = 'trunk_v2.0/'

# Call the function to list file types
file_types = list_file_types(directory_to_search)

# Print the list of file types
print("List of file types:")
for file_type in file_types:
    print(file_type)

# result
list_file_to_blame = ['sci','gms','py','txt','R','sh','c']

