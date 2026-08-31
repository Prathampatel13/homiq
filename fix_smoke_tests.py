import os, glob

for f in glob.glob('backend/tests/smoke/*smoke_test.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('r"c:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend"', 'str(Path(__file__).resolve().parent.parent.parent)')
    # also add from pathlib import Path if not there
    if 'from pathlib import Path' not in content:
        content = content.replace('import sys', 'import sys\nfrom pathlib import Path')
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
