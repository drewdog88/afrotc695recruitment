#!/usr/bin/env python3
"""
Extract all table data from the Word document
"""

import docx

def extract_table_data():
    """Extract all table data from the document"""
    
    doc = docx.Document('Jesuit and Catholic High Schools in Seattle and Portland.docx')
    
    print("=== EXTRACTING ALL TABLE DATA ===")
    
    for i, table in enumerate(doc.tables):
        print(f"\nTable {i+1} ({len(table.rows)} rows):")
        print("-" * 50)
        
        for j, row in enumerate(table.rows):
            row_data = [cell.text.strip() for cell in row.cells]
            print(f"Row {j+1}: {row_data}")
            
            # If this looks like a school entry, print it more clearly
            if any(keyword in ' '.join(row_data).lower() for keyword in ['school', 'academy', 'prep', 'jesuit', 'catholic']):
                print(f"  *** POTENTIAL SCHOOL ENTRY ***")
                for k, cell in enumerate(row_data):
                    if cell:
                        print(f"    Cell {k+1}: {cell}")

if __name__ == "__main__":
    extract_table_data()
