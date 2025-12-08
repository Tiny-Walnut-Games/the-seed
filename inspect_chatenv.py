#!/usr/bin/env python3
from datasets import load_dataset
import json

print("Loading SustcZhangYX/ChatEnv dataset...")
ds = load_dataset("SustcZhangYX/ChatEnv")

print("Splits:", list(ds.keys()))
split_name = list(ds.keys())[0]
print(f"\nFirst split: {split_name}")
print(f"Number of items: {len(ds[split_name])}")

item = ds[split_name][0]
print(f"\nFirst item keys: {list(item.keys())}")
print(f"\nFirst item sample:")
print(json.dumps({k: str(v)[:200] if isinstance(v, str) else v for k, v in item.items()}, indent=2))

# Check a few more items to understand structure
print(f"\n\nChecking structure of first 3 items:")
for i in range(min(3, len(ds[split_name]))):
    item = ds[split_name][i]
    print(f"\nItem {i} keys: {list(item.keys())}")
    for key in item.keys():
        val = item[key]
        if isinstance(val, str):
            print(f"  {key}: {val[:100]}...")
        elif isinstance(val, list):
            print(f"  {key}: list with {len(val)} items")
            if val and isinstance(val[0], dict):
                print(f"    First item keys: {list(val[0].keys())}")
        else:
            print(f"  {key}: {type(val).__name__}")
