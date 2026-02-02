#!/usr/bin/env python3
"""
Main script to process ChatGPT export and generate organized JSON for the dashboard.

Usage:
    python run.py <path_to_chat.html>

Or place your chat.html in this directory and run:
    python run.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).parent

    # Check for chat.html
    if len(sys.argv) > 1:
        chat_file = Path(sys.argv[1])
        if not chat_file.exists():
            print(f"Error: File not found: {chat_file}")
            sys.exit(1)
        # Copy to script directory if not already there
        if chat_file.parent != script_dir:
            import shutil
            dest = script_dir / "chat.html"
            print(f"Copying {chat_file} to {dest}...")
            shutil.copy(chat_file, dest)
    else:
        chat_file = script_dir / "chat.html"
        if not chat_file.exists():
            print("Error: No chat.html found.")
            print("\nUsage:")
            print("  python run.py <path_to_chat.html>")
            print("  or place chat.html in this directory and run: python run.py")
            print("\nTo get chat.html:")
            print("  1. Go to ChatGPT Settings > Data controls > Export data")
            print("  2. Download and extract the zip file")
            print("  3. Use the chat.html file from the export")
            sys.exit(1)

    print("=" * 50)
    print("ChatGPT History Dashboard Generator")
    print("=" * 50)

    # Step 1: Parse chat.html
    print("\n[1/3] Parsing chat.html...")
    result = subprocess.run([sys.executable, str(script_dir / "parse_chat.py")], cwd=script_dir)
    if result.returncode != 0:
        print("Error: Failed to parse chat.html")
        sys.exit(1)

    # Step 2: Classify into categories
    print("\n[2/3] Classifying into categories...")
    result = subprocess.run([sys.executable, str(script_dir / "classify_categories.py")], cwd=script_dir)
    if result.returncode != 0:
        print("Error: Failed to classify categories")
        sys.exit(1)

    # Step 3: Group into topics
    print("\n[3/3] Grouping Q&As into topics...")
    result = subprocess.run([sys.executable, str(script_dir / "group_topics.py")], cwd=script_dir)
    if result.returncode != 0:
        print("Error: Failed to group topics")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Done! To view the dashboard:")
    print("=" * 50)
    print(f"\n  cd {script_dir}")
    print("  python -m http.server 8080")
    print("\n  Then open: http://localhost:8080/dashboard.html")
    print()


if __name__ == "__main__":
    main()
