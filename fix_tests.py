import re

# Fix test_new_mit_datasets.py
with open(r'warbler-cda-package\tests\test_new_mit_datasets.py', 'r') as f:
    content = f.read()

# 1. Add import time to imports section
if 'import time\n' not in content[:200]:
    content = content.replace(
        'import pytest\nfrom warbler_cda',
        'import time\nimport pytest\nfrom warbler_cda'
    )

# 2. Remove import time from inside the function (line 527)
content = content.replace(
    '            import time\n\n            start',
    '            start'
)

# 3. Fix implicit string concatenation (line 287)
content = content.replace(
    '"warbler_cda.utils.transformers" ".portuguese_education.load_dataset"',
    '"warbler_cda.utils.transformers.portuguese_education.load_dataset"'
)

# 4. Fix mock_dataset reassignments
lines = content.split('\n')
i = 0
while i < len(lines):
    if 'mock_dataset = MagicMock()' in lines[i]:
        if i + 1 < len(lines) and 'mock_dataset = [mock_' in lines[i+1]:
            # Replace the reassignment
            lines[i+1] = lines[i+1].replace('mock_dataset = [', 'mock_dataset.__getitem__.return_value = [')
    i += 1

content = '\n'.join(lines)

with open(r'warbler-cda-package\tests\test_new_mit_datasets.py', 'w') as f:
    f.write(content)

print("Fixed test_new_mit_datasets.py")

# Fix test_pdf_ingestion.py
with open(r'warbler-cda-package\tests\test_pdf_ingestion.py', 'r') as f:
    content = f.read()

# 1. Fix docstring - add period
content = content.replace(
    '"""Test suite for PDF-based dataset ingestion\n\nTests for handling datasets with PDF fields instead of text content.\nIncludes fallback handling when PDF extraction is unavailable.\n"""',
    '"""Test suite for PDF-based dataset ingestion.\n\nTests for handling datasets with PDF fields instead of text content.\nIncludes fallback handling when PDF extraction is unavailable.\n"""'
)

# 2. Remove unused imports
content = content.replace('import pytest\n', '')
content = content.replace('import json\n', '')
content = content.replace('from unittest.mock import Mock, patch, MagicMock\n', 'from unittest.mock import patch, MagicMock\n')
content = content.replace('from typing import Dict, List, Any\n', '')

# 3. Move sys.path.insert to after all imports
lines = content.split('\n')
new_lines = []
sys_path_line = None

for i, line in enumerate(lines):
    if 'sys.path.insert' in line:
        sys_path_line = line
    elif sys_path_line and line.startswith('from warbler_cda'):
        # Insert sys_path_line before this line
        new_lines.append(sys_path_line)
        sys_path_line = None
        new_lines.append(line)
    elif not 'sys.path.insert' in line:
        new_lines.append(line)

if sys_path_line:
    new_lines.append(sys_path_line)

content = '\n'.join(new_lines)

# 4. Add periods to docstrings
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('"""Test') and line.strip().endswith('"""') and not line.strip().endswith('."""'):
        if '"""' in line:
            # Find the last """ and add period before it
            if line.rstrip().endswith('"""') and not line.rstrip().endswith('."""'):
                line = line.rstrip()[:-3] + '."""'
                lines[i] = line

content = '\n'.join(lines)

with open(r'warbler-cda-package\tests\test_pdf_ingestion.py', 'w') as f:
    f.write(content)

print("Fixed test_pdf_ingestion.py")
