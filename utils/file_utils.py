# utils/file_utils.py

import os

def read_file_lines(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.readlines()

def write_file_lines(filepath, lines):
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(lines)
