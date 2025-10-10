"""
Script to remove emoji and non-ASCII characters from CLI files
and replace them with ASCII-safe symbols for Windows console compatibility.
"""

import os
import glob

# Define emoji replacements
replacements = {
    '✅': '[OK]',
    '❌': '[FAILED]',
    '🔍': '[*]',
    '⚠️': '[!]',
    '⚠': '[!]',
    '🎉': '[SUCCESS]',
    '📊': '[INFO]',
    '🗑️': '[DEL]',
    '✓': '[OK]',
    '✗': '[X]',
    '►': '>',
    '▶': '>',
    '⚙️': '[*]',
    '🏗️': '[*]',
    '🏷️': '[*]',
}

def replace_emoji_in_file(filepath):
    """Replace all emoji in a file with ASCII-safe symbols."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for emoji, replacement in replacements.items():
            content = content.replace(emoji, replacement)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        else:
            print(f"- No changes: {filepath}")
            return False
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    # Get all Python files in the CLI directory
    cli_dir = os.path.join(os.path.dirname(__file__), '..', 'purviewcli', 'cli')
    py_files = glob.glob(os.path.join(cli_dir, '*.py'))
    
    print(f"Processing {len(py_files)} files in {cli_dir}...\n")
    
    updated_count = 0
    for filepath in sorted(py_files):
        if replace_emoji_in_file(filepath):
            updated_count += 1
    
    print(f"\nSummary: Updated {updated_count} out of {len(py_files)} files")

if __name__ == '__main__':
    main()
