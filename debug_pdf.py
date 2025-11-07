#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/backend/app')

from parsers.pdf_parser import PDFParser

pdf_path = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/examples/treatments/Tatort_SaltoMortale_Treatment_2025-08.pdf"

with open(pdf_path, 'rb') as f:
    content = f.read()

parser = PDFParser(content)
text = parser.extract_text()

# Show first 2000 characters
print("="*60)
print("EXTRACTED TEXT (first 2000 chars):")
print("="*60)
print(repr(text[:2000]))
print("\n")

# Count newlines
print("="*60)
print("STATISTICS:")
print("="*60)
print(f"Total length: {len(text)}")
print(f"Single newlines (\\n): {text.count(chr(10))}")
print(f"Double newlines (\\n\\n): {text.count(chr(10)+chr(10))}")
print(f"Words: {len(text.split())}")

# Extract scenes
scenes = parser.extract_scenes()
print(f"\nScenes extracted: {len(scenes)}")
if scenes:
    print(f"First scene preview: {scenes[0]['text'][:200]}...")
