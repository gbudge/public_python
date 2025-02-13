#!/usr/bin/env python3

import glob
import os

# Define the include and exclude patterns using space-separated glob patterns
include_patterns = 'files/**/*.txt,files/**/*.docx'
exclude_patterns = '.github/**,.vscode/**'

# Find all files that match any of the include patterns
include_pattern_files = set()
for pattern in include_patterns.split(','):
    files = glob.glob(pattern, recursive=True)
    include_pattern_files.update([f for f in files if os.path.isfile(f)])

# Find all files that match any of the exclude patterns
exclude_pattern_files = set()
for pattern in exclude_patterns.split(','):
    files = glob.glob(pattern, recursive=True)
    exclude_pattern_files.update([f for f in files if os.path.isfile(f)])

# Files that match include patterns but not exclude patterns
final_candidate_files = include_pattern_files - exclude_pattern_files

print(f"include_pattern_files: {include_pattern_files}")
print(f"exclude_pattern_files: {exclude_pattern_files}")
print(f"final_candidate_files: {final_candidate_files}")

# If pull_request_files.txt exists, filter based on it
pull_request_files = 'pull_request_files.txt'
if os.path.exists(pull_request_files):
    with open(pull_request_files, 'r') as f:
        files = set(f.read().splitlines())
    
    print(f"pull_request_files:    {files}")
    filtered_files_to_scan = [f for f in final_candidate_files if f in files]
else:
    filtered_files_to_scan = set(final_candidate_files)

# Set env.RUN_SCANNER to false if no files are found to scan
if not filtered_files_to_scan:
    print("No files found to scan.")
else:
    print(f"Files to scan: {filtered_files_to_scan}")

