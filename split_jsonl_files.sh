#!/bin/bash

# Function to split the file
split_file() {
    file="$1"
    max_size="80M"  # Hardcoded to 80MB
    output_dir="$2"
    
    # Get the base filename without extension
    base_filename=$(basename "$file" | cut -d. -f1)
    
    # Get the extension of the file
    extension="${file##*.}"
    
    # Create the output directory if it doesn't exist
    mkdir -p "$output_dir"
    
    # Split the file into smaller parts
    split -C "$max_size" --numeric-suffixes --additional-suffix=".$extension" "$file" "$output_dir/$base_filename.split"
}

# Check if the file is provided as an argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <file> [output_dir]"
    exit 1
fi

# Get the file and output directory from the command line arguments
file="$1"
output_dir="$2"

# Check if the file exists
if [ ! -f "$file" ]; then
    echo "File not found: $file"
    exit 1
fi

# Call the split_file function
split_file "$file" "$output_dir"