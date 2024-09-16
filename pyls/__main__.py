import json
import argparse
import os
from datetime import datetime
from typing import List, Dict, Union

# Utility function to read JSON file
def read_json(filename: str) -> Dict:
    with open(filename, 'r') as file:
        return json.load(file)

# Utility function to format file sizes in human-readable format
def human_readable_size(size: int) -> str:
    if size >= 1_073_741_824:
        return f"{size / 1_073_741_824:.1f}G"
    elif size >= 1_048_576:
        return f"{size / 1_048_576:.1f}M"
    elif size >= 1_024:
        return f"{size / 1_024:.1f}K"
    else:
        return str(size)

# Format timestamp into human-readable date
def format_time(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%b %d %H:%M")

# Helper function to filter and sort files
def filter_sort_files(files: List[Dict], filter_type: str, reverse: bool, sort_by: str) -> List[Dict]:
    if filter_type == 'file':
        files = [f for f in files if f['permissions'][0] == '-']
    elif filter_type == 'dir':
        files = [f for f in files if f['permissions'][0] == 'd']
    else:
        raise ValueError("Invalid filter type")
    
    sort_key = {'size': 'size', 'time': 'time_modified'}[sort_by]
    files.sort(key=lambda x: x[sort_key], reverse=reverse)
    return files

# Recursive function to list files in the directory
def list_files(data: Dict, args: argparse.Namespace, path: str) -> None:
    items = data.get('contents', [])
    if args.filter:
        items = filter_sort_files(items, args.filter, args.reverse, args.sort)
    
    for item in items:
        if not args.A and item['name'].startswith('.'):
            continue
        
        if args.l:
            size = human_readable_size(item['size']) if args.human else item['size']
            time = format_time(item['time_modified'])
            print(f"{item['permissions']} {size} {time} {item['name']}")
        else:
            print(item['name'])
        
        if args.l and item.get('contents'):
            list_files(item, args, os.path.join(path, item['name']))

# Main function to handle argument parsing and execution
def main():
    parser = argparse.ArgumentParser(description="List directory contents")
    parser.add_argument("path", nargs='?', default='', help="Path to the directory")
    parser.add_argument("-A", action="store_true", help="List all entries including hidden files")
    parser.add_argument("-l", action="store_true", help="Use a long listing format")
    parser.add_argument("-r", action="store_true", help="Reverse the order of the sort")
    parser.add_argument("-t", action="store_true", help="Sort by time modified")
    parser.add_argument("--filter", choices=['file', 'dir'], help="Filter by type")
    parser.add_argument("--human", action="store_true", help="Show human-readable file sizes")
    parser.add_argument("--helpp", action="help", help="Show this help message and exit")
    
    args = parser.parse_args()

    # Load the JSON data
    paths = os.getcwd()
    strupath = paths + "\pyls\structure.json"

    data = read_json("structure.json")
    
    # Determine the directory to list
    if args.path:
        path_parts = args.path.split('/')
        current = data
        for part in path_parts:
            if part:
                found = next((item for item in current.get('contents', []) if item['name'] == part), None)
                if found:
                    current = found
                else:
                    print(f"error: cannot access '{args.path}': No such file or directory")
                    return
    else:
        current = data
    
    list_files(current, args, args.path)

if __name__ == "__main__":
    main()
