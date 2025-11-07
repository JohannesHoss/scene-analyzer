#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/backend/app')

from parsers.txt_parser import TXTParser

txt_path = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/test_screenplay.txt"

with open(txt_path, 'rb') as f:
    content = f.read()

parser = TXTParser(content)
text = parser.extract_text()

print("="*60)
print("TEXT PREVIEW (first 500 chars):")
print("="*60)
print(text[:500])
print("\n")

# Extract scenes
scenes = parser.extract_scenes()
print("="*60)
print(f"SCENES EXTRACTED: {len(scenes)}")
print("="*60)

for i, scene in enumerate(scenes[:5], 1):
    print(f"\nScene {i}:")
    print(f"  INT/EXT: {scene.get('int_ext', '?')}")
    print(f"  Location: {scene.get('location', '?')}")
    print(f"  Time: {scene.get('time_of_day', '?')}")
    print(f"  Text preview: {scene['text'][:100]}...")
