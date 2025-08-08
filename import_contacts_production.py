#!/usr/bin/env python3
"""
Import the parsed contact data into the production database
"""

import sys
import os
sys.path.append('api')

# Use production app configuration
from app import app, db, UniversityContact
from parse_contacts import parse_contact_data

def drop_all_contacts():
    """Drop all existing outreach contacts"""
    print("=== DROPPING EXISTING CONTACTS (PRODUCTION) ===")
    
    with app.app_context():
        # Delete all existing contacts
        deleted_count = UniversityContact.query.delete()
        db.session.commit()
        print(f"Deleted {deleted_count} existing contacts")
        print()

def import_contacts():
    """Import the parsed contact data"""
    print("=== IMPORTING NEW CONTACTS (PRODUCTION) ===")
    
    contacts = parse_contact_data()
    
    with app.app_context():
        imported_count = 0
        
        for contact_data in contacts:
            try:
                # Create new contact
                new_contact = UniversityContact(
                    university_name=contact_data['university_name'],
                    contact_name=contact_data['contact_name'],
                    contact_title=contact_data['contact_title'],
                    email=contact_data['email'],
                    phone=contact_data['phone'],
                    address=contact_data['address'],
                    notes=contact_data['notes']
                )
                
                db.session.add(new_contact)
                imported_count += 1
                
                print(f"✓ {contact_data['university_name']}")
                
            except Exception as e:
                print(f"✗ Error importing {contact_data['university_name']}: {e}")
        
        # Commit all changes
        db.session.commit()
        print(f"\nSuccessfully imported {imported_count} contacts")
        print()

def verify_import():
    """Verify the import worked correctly"""
    print("=== VERIFYING IMPORT (PRODUCTION) ===")
    
    with app.app_context():
        all_contacts = UniversityContact.query.all()
        print(f"Total contacts in database: {len(all_contacts)}")
        print()
        
        print("Imported contacts:")
        print("-" * 50)
        for i, contact in enumerate(all_contacts, 1):
            print(f"{i}. {contact.university_name}")
            print(f"   Contact: {contact.contact_name} ({contact.contact_title})")
            print(f"   Email: {contact.email}")
            print(f"   Phone: {contact.phone}")
            print(f"   Location: {contact.address}")
            print()

def main():
    """Main import process"""
    print("=== PRODUCTION CONTACT IMPORT PROCESS ===")
    print()
    
    # Step 1: Drop existing data
    drop_all_contacts()
    
    # Step 2: Import new data
    import_contacts()
    
    # Step 3: Verify import
    verify_import()
    
    print("=== PRODUCTION IMPORT COMPLETE ===")

if __name__ == "__main__":
    main()
