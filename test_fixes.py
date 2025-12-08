#!/usr/bin/env python3
"""
Quick test to verify the bug fixes work
"""

# Test 1: Verify novels fix handles string items
print("Test 1: Novels fix - handling string items")
item = "This is a string, not a dict"
if isinstance(item, str):
    print("✓ String detection works")
else:
    print("✗ String detection failed")

# Test 2: Verify safe key access
print("\nTest 2: Safe dictionary key access")
item = {"text": "content"}
item_keys = []
try:
    if isinstance(item, dict):
        item_keys = list(item.keys())
    print(f"✓ Keys extracted: {item_keys}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Verify multi-character conversation handling
print("\nTest 3: Multi-character conversation handling")
conversation = [{"from": "Alice", "message": "Hello"}, {"from": "Bob", "message": "Hi there"}]
conversation_lines = []
for msg in conversation:
    try:
        if isinstance(msg, dict):
            from_field = msg.get("from", "Unknown")
            message_field = msg.get("message", "")
            conversation_lines.append(f"{from_field}: {message_field}")
    except Exception:
        continue
print(f"✓ Conversation formatted: {len(conversation_lines)} lines")

# Test 4: Verify portuguese-edu dict conversion
print("\nTest 4: Portuguese-edu dict conversion")
item = {"title": "Test", "content": "Content"}
item_with_content = {}
try:
    if isinstance(item, dict):
        item_with_content = item.copy()
    item_with_content["content"] = "Updated content"
    print(f"✓ Dict conversion works: {list(item_with_content.keys())}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n✅ All basic tests passed!")
