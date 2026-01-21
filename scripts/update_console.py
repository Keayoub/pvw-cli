"""Update all CLI files to use smart console utility"""
import re
import glob

files = glob.glob('purviewcli/cli/*.py')
pattern1 = r'from rich\.console import Console\n\nconsole = Console\(legacy_windows=False\)'
pattern2 = r'from rich\.console import Console\n\n\nconsole = Console\(legacy_windows=False\)'
replacement = 'from .console_utils import get_console\n\nconsole = get_console()'

updated = []
for f in files:
    if f in ['purviewcli/cli/console_utils.py', 'purviewcli/cli/cli.py', 'purviewcli/cli/account.py']:
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    original = content
    content = re.sub(pattern1, replacement, content)
    content = re.sub(pattern2, replacement.replace('\n\n', '\n\n\n'), content)
    if content != original:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        updated.append(f)
        
print(f'Updated {len(updated)} files')
for f in updated:
    print(f'  - {f}')
