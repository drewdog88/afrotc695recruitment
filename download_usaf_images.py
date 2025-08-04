#!/usr/bin/env python3
"""
US Air Force Background Image Setup Script

This script helps download and optimize authentic US Air Force public domain images
from DVIDS for use as subtle page backgrounds in the AFROTC 695 recruitment system.

All images are public domain works of the United States Air Force.
"""

import os
import sys
from PIL import Image
import requests
from pathlib import Path

# Image configuration
IMAGES = {
    'f22_raptor.jpg': {
        'url': 'https://www.dvidshub.net/image/8582415/us-f-22s-land-basa-air-base-philippines-during-dfe-operations',
        'virin': '240808-F-TK526-1147',
        'description': 'F-22 Raptor - Used for Recruits page',
        'direct_download': None  # DVIDS requires login for downloads
    },
    'f22_formation.jpg': {
        'url': 'https://www.dvidshub.net/image/8585844/us-f-22s-land-mactan-benito-ebuen-air-base-philippines-during-dfe-operations',
        'virin': '240809-F-TK526-1242',
        'description': 'F-22 Formation - Used for Cadets and Login pages',
        'direct_download': None
    },
    'b52_aerial_refuel.jpg': {
        'url': 'https://www.dvidshub.net/image/8219744/aerial-refueling-b-52',
        'virin': '240130-F-WT071-1013',
        'description': 'B-52 Aerial Refueling - Used for Contacts page',
        'direct_download': None
    },
    'b52_formation.jpg': {
        'url': 'https://www.dvidshub.net/image/8904378/b-52h-stratofortress-joins-formation-during-btf-25-2',
        'virin': '250306-F-AE827-1059',
        'description': 'B-52 Formation - Used for Calendar page',
        'direct_download': None
    },
    'kc135_international.jpg': {
        'url': 'https://www.dvidshub.net/image/3816877/international-aerial-refuel',
        'virin': '170925-F-QF982-0255',
        'description': 'KC-135 International Refueling - Used for Materials page',
        'direct_download': None
    },
    'b1_lancer.jpg': {
        'url': 'https://www.dvidshub.net/image/8646233/37th-bomb-squadron-exercise-takeoff',
        'virin': '240916-F-DW056-3826',
        'description': 'B-1B Lancer - Used for Admin page',
        'direct_download': None
    },
    'b52_kc10_refuel.jpg': {
        'url': 'https://www.dvidshub.net/image/2948867/kc-10-extender-maintains-decisive-air-power',
        'virin': '161026-F-CO490-015',
        'description': 'B-52 with KC-10 - Used for System Statistics page',
        'direct_download': None
    }
}

def optimize_image(input_path, output_path, max_width=1920, quality=85):
    """
    Optimize an image for web use as a background.
    
    Args:
        input_path: Path to the input image
        output_path: Path to save the optimized image
        max_width: Maximum width in pixels
        quality: JPEG quality (1-100)
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # Get file size
            size_kb = os.path.getsize(output_path) / 1024
            print(f"✓ Optimized {output_path.name}: {img.width}x{img.height}, {size_kb:.1f}KB")
            
    except Exception as e:
        print(f"✗ Error optimizing {input_path}: {e}")

def main():
    """Main function to set up USAF background images."""
    print("🇺🇸 US Air Force Background Image Setup")
    print("=" * 50)
    print()
    
    # Create backgrounds directory
    bg_dir = Path("static/backgrounds")
    bg_dir.mkdir(parents=True, exist_ok=True)
    
    print("📋 Required Images:")
    print()
    
    for filename, info in IMAGES.items():
        print(f"📸 {filename}")
        print(f"   Description: {info['description']}")
        print(f"   DVIDS URL: {info['url']}")
        print(f"   VIRIN: {info['virin']}")
        print()
    
    print("📥 Download Instructions:")
    print("1. Visit each DVIDS URL above")
    print("2. Click 'Register/Login to Download' (free DVIDS account required)")
    print("3. Download the highest resolution version available")
    print("4. Place the downloaded images in the 'downloads' folder")
    print("5. Run this script with --optimize to process them")
    print()
    
    # Check for --optimize flag
    if '--optimize' in sys.argv:
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            print("❌ Downloads folder not found. Please create 'downloads' folder and add images.")
            return
        
        print("🔧 Optimizing images...")
        print()
        
        optimized_count = 0
        for filename in IMAGES.keys():
            input_file = downloads_dir / filename
            output_file = bg_dir / filename
            
            if input_file.exists():
                optimize_image(input_file, output_file)
                optimized_count += 1
            else:
                print(f"⚠️  {filename} not found in downloads folder")
        
        print()
        print(f"✅ Optimized {optimized_count} images")
        
        if optimized_count > 0:
            print()
            print("🎨 Background system is now active!")
            print("   - Different pages will show different Air Force aircraft")
            print("   - Backgrounds are subtle and won't interfere with readability")
            print("   - Works with both Original and Air Force themes")
    
    else:
        print("💡 To optimize downloaded images, run:")
        print("   python download_usaf_images.py --optimize")

if __name__ == "__main__":
    main()