#!/usr/bin/env python3
"""
🧙‍♂️ Bootstrap Sentinel's Import Fixer
Adds missing compatibility imports to files that use the extension methods
"""

import os
import glob

print("🔧 Adding missing compatibility imports...")

cs_files = glob.glob('Assets/**/*.cs', recursive=True)

for file_path in cs_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        needs_import = (
            ('SetBorderRadius' in content or 'SetBorderWidth' in content or 'SetBorderColor' in content) 
            and 'using MobileGameTemplate.Core;' not in content
            and 'using UnityEngine.UIElements;' in content
        )
        
        if needs_import:
            # Add the import after UIElements
            content = content.replace(
                'using UnityEngine.UIElements;', 
                'using UnityEngine.UIElements;\nusing MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility Bridge'
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Added compatibility import to {os.path.basename(file_path)}')
    
    except Exception as e:
        print(f'❌ Error processing {file_path}: {e}')

print("🎉 Import fixes complete!")
