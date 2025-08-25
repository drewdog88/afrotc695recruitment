#!/usr/bin/env python3
"""
Clean up Vercel Blob references from the codebase
This script identifies and reports any remaining Vercel Blob references that should be removed
"""

import os
import re
from pathlib import Path

def find_vercel_blob_references():
    """Find all files that contain Vercel Blob references"""
    print("🔍 Scanning for Vercel Blob references...")
    print("=" * 60)

    # Patterns to search for
    patterns = [
        r'vercel_blob',
        r'BLOB_READ_WRITE_TOKEN',
        r'blob\.vercel-storage\.com',
        r'from vercel_blob',
        r'import vercel_blob',
        r'Vercel Blob',
        r'vercel.*blob',
        r'blob.*vercel'
    ]

    # File extensions to check
    extensions = ['.py', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.js']

    # Directories to skip
    skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', '.env'}

    found_references = []

    for root, dirs, files in os.walk('.'):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = Path(root) / file

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            found_references.append({
                                'file': str(file_path),
                                'pattern': pattern,
                                'line': content[:match.start()].count('\n') + 1,
                                'context': content[max(0, match.start()-50):match.end()+50].replace('\n', ' ')
                            })

                except Exception as e:
                    print(f"⚠️  Error reading {file_path}: {e}")

    return found_references

def categorize_references(references):
    """Categorize references by type and importance"""
    categories = {
        'critical': [],      # Must be removed/fixed
        'documentation': [], # Documentation references
        'legacy': [],        # Legacy code that can be removed
        'test': [],          # Test files
        'config': []         # Configuration files
    }

    for ref in references:
        file_path = ref['file']

        if 'test' in file_path.lower():
            categories['test'].append(ref)
        elif file_path.endswith('.md') or 'readme' in file_path.lower():
            categories['documentation'].append(ref)
        elif 'backup' in file_path.lower() or 'legacy' in file_path.lower():
            categories['legacy'].append(ref)
        elif file_path.endswith(('.json', '.yaml', '.yml')):
            categories['config'].append(ref)
        else:
            categories['critical'].append(ref)

    return categories

def print_report(categories):
    """Print a detailed report of found references"""
    print("\n📊 VERCEL BLOB REFERENCES REPORT")
    print("=" * 60)

    total_refs = sum(len(refs) for refs in categories.values())
    print(f"Total references found: {total_refs}")

    for category, refs in categories.items():
        if refs:
            print(f"\n🔴 {category.upper()} REFERENCES ({len(refs)}):")
            print("-" * 40)

            for ref in refs:
                print(f"📄 {ref['file']}:{ref['line']}")
                print(f"   Pattern: {ref['pattern']}")
                print(f"   Context: ...{ref['context']}...")
                print()

    print("\n💡 RECOMMENDATIONS:")
    print("-" * 40)

    if categories['critical']:
        print("🔴 CRITICAL: Remove or update these references immediately")
        for ref in categories['critical']:
            print(f"   - {ref['file']}:{ref['line']}")

    if categories['legacy']:
        print("\n🟡 LEGACY: Consider removing these legacy files")
        for ref in categories['legacy']:
            print(f"   - {ref['file']}")

    if categories['documentation']:
        print("\n📚 DOCUMENTATION: Update documentation to reflect R2 usage")
        for ref in categories['documentation']:
            print(f"   - {ref['file']}")

    if categories['test']:
        print("\n🧪 TESTS: Update test files to use R2 instead of Vercel Blob")
        for ref in categories['test']:
            print(f"   - {ref['file']}")

def main():
    """Main function"""
    print("🧹 Vercel Blob Reference Cleanup Tool")
    print("=" * 60)
    print("This tool identifies remaining Vercel Blob references in the codebase.")
    print("After migrating to Cloudflare R2, these should be cleaned up.\n")

    # Find references
    references = find_vercel_blob_references()

    if not references:
        print("✅ No Vercel Blob references found! The codebase is clean.")
        return

    # Categorize references
    categories = categorize_references(references)

    # Print report
    print_report(categories)

    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Review critical references and update them to use R2")
    print("2. Remove legacy backup files that reference Vercel Blob")
    print("3. Update documentation to reflect R2 usage")
    print("4. Update test files to use R2 instead of Vercel Blob")
    print("5. Run this script again to verify cleanup")

if __name__ == "__main__":
    main()
