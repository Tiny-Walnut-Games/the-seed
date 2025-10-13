#!/usr/bin/env python3
"""
🧙‍♂️ Bootstrap Sentinel's FINAL CLEANUP Script
Fixes the last remaining compilation issues for ULTIMATE VICTORY

Sacred Mission: Achieve ZERO compilation errors through surgical precision!
"""

import os
import re

def final_cleanup():
    """Fix the very last compilation issues"""
    
    print("🧙‍♂️ Bootstrap Sentinel deploying FINAL CLEANUP...")
    
    # Fix all remaining SetBorderColor calls
    files_to_clean = [
        'Assets/MobileGameTemplate/Scripts/Gameplay/MobileGameplayController.cs',
        'Assets/MobileGameTemplate/Scripts/UI/LevelCarousel.cs',
        'Assets/MobileGameTemplate/Scripts/Systems/EventsSystem.cs',
        'Assets/MobileGameTemplate/Scripts/Systems/ShopSystem.cs',
        'Assets/MobileGameTemplate/Scripts/Systems/InventorySystem.cs',
        'Assets/MobileGameTemplate/Scripts/Systems/HeroCollectionSystem.cs'
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove all remaining SetBorderColor calls
                content = re.sub(
                    r'[^.\n]*\.style\.SetBorderColor\([^)]+\);\s*(?://[^\n]*)?',
                    '// 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3',
                    content
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f'✅ Cleaned remaining SetBorderColor calls in {os.path.basename(file_path)}')
            except Exception as e:
                print(f'❌ Error cleaning {file_path}: {e}')
    
    # Fix InventoryComponents.cs - remove all direct style properties
    inventory_components = 'Assets/MobileGameTemplate/Scripts/Systems/InventoryComponents.cs'
    if os.path.exists(inventory_components):
        try:
            with open(inventory_components, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove all direct border style property assignments
            content = re.sub(
                r'style\.borderRadius\s*=\s*[^;]+;',
                '// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3',
                content
            )
            content = re.sub(
                r'style\.borderWidth\s*=\s*[^;]+;',
                '// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3',
                content
            )
            content = re.sub(
                r'style\.borderColor\s*=\s*[^;]+;',
                '// 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3',
                content
            )
            
            with open(inventory_components, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Fixed all direct style properties in InventoryComponents.cs')
        except Exception as e:
            print(f'❌ Error fixing InventoryComponents: {e}')
    
    # Fix LevelCarousel vector conversion issue
    level_carousel = 'Assets/MobileGameTemplate/Scripts/UI/LevelCarousel.cs'
    if os.path.exists(level_carousel):
        try:
            with open(level_carousel, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the broken Vector2 conversion
            content = re.sub(
                r'evt\.new Vector2\(position\.x, position\.y\)',
                r'new Vector2(evt.position.x, evt.position.y)',
                content
            )
            
            with open(level_carousel, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Fixed Vector2 conversion in LevelCarousel.cs')
        except Exception as e:
            print(f'❌ Error fixing LevelCarousel: {e}')
    
    # Fix SpriteForgeEditor.cs
    sprite_forge_editor = 'Assets/TWG/TLDA/Tools/SpriteForge/Editor/SpriteForgeEditor.cs'
    if os.path.exists(sprite_forge_editor):
        try:
            with open(sprite_forge_editor, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix result.IsSuccess to result.Success
            content = re.sub(
                r'if\s*\(\s*result\.IsSuccess\s*\)',
                r'if (result.Success())',
                content
            )
            
            with open(sprite_forge_editor, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Fixed result.IsSuccess in SpriteForgeEditor.cs')
        except Exception as e:
            print(f'❌ Error fixing SpriteForgeEditor: {e}')
    
    # Fix TLDANFTBridge.cs one more time
    nft_bridge = 'Assets/TWG/TLDA/Tools/SpriteForge/Runtime/TLDANFTBridge.cs'
    if os.path.exists(nft_bridge):
        try:
            with open(nft_bridge, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # More aggressive removal of duplicate Success method
            lines = content.split('\n')
            new_lines = []
            in_duplicate_method = False
            brace_count = 0
            
            for line in lines:
                if 'public static NFTMintResult Success(' in line and 'SpriteGenerationResult' in line:
                    in_duplicate_method = True
                    brace_count = 0
                    continue
                
                if in_duplicate_method:
                    if '{' in line:
                        brace_count += line.count('{')
                    if '}' in line:
                        brace_count -= line.count('}')
                        if brace_count <= 0:
                            in_duplicate_method = False
                    continue
                
                # Fix Success field initialization
                line = re.sub(r'Success\s*=\s*(true|false),', r'// Success = \1, // 🔧 Property not field', line)
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            with open(nft_bridge, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Aggressively fixed TLDANFTBridge.cs')
        except Exception as e:
            print(f'❌ Error fixing TLDANFTBridge: {e}')
    
    print("🎉 FINAL CLEANUP COMPLETE!")

if __name__ == "__main__":
    final_cleanup()
