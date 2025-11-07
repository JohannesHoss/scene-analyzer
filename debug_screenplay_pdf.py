#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/backend/app')

from parsers.pdf_parser import PDFParser

pdf_path = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/examples/screenplays/WreckingBall_Screenplay_2025-10.pdf"

with open(pdf_path, 'rb') as f:
    content = f.read()

parser = PDFParser(content)
text = parser.extract_text()

print("="*60)
print("TEXT PREVIEW (first 1000 chars):")
print("="*60)
print(repr(text[:1000]))
print("\n")

print("="*60)
print("STATISTICS:")
print("="*60)
print(f"Total length: {len(text)}")
print(f"Single newlines (\\n): {text.count(chr(10))}")
print(f"Double newlines (\\n\\n): {text.count(chr(10)+chr(10))}")
print(f"Lines with INT. or EXT.: {sum(1 for line in text.split(chr(10)) if 'INT.' in line or 'EXT.' in line)}")
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
