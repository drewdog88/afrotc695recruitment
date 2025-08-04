# US Air Force Background Images

This directory contains authentic US Air Force public domain images for use as subtle page backgrounds.

## Image Sources (All Public Domain from DVIDS)

### Fighter Aircraft
1. **f22_raptor.jpg** - F-22 Raptor
   - Source: https://www.dvidshub.net/image/8582415/us-f-22s-land-basa-air-base-philippines-during-dfe-operations
   - VIRIN: 240808-F-TK526-1147
   - Resolution: 6555x2872

2. **f22_formation.jpg** - F-22 Formation Flight
   - Source: https://www.dvidshub.net/image/8585844/us-f-22s-land-mactan-benito-ebuen-air-base-philippines-during-dfe-operations
   - VIRIN: 240809-F-TK526-1242
   - Resolution: 6260x3324

### Strategic Bombers
3. **b52_aerial_refuel.jpg** - B-52 Aerial Refueling
   - Source: https://www.dvidshub.net/image/8219744/aerial-refueling-b-52
   - VIRIN: 240130-F-WT071-1013
   - Resolution: 4128x2752

4. **b52_formation.jpg** - B-52 Formation Flight
   - Source: https://www.dvidshub.net/image/8904378/b-52h-stratofortress-joins-formation-during-btf-25-2
   - VIRIN: 250306-F-AE827-1059
   - Resolution: 6048x4024

5. **b52_kc10_refuel.jpg** - B-52 with KC-10 Extender
   - Source: https://www.dvidshub.net/image/2948867/kc-10-extender-maintains-decisive-air-power
   - VIRIN: 161026-F-CO490-015
   - Resolution: 4928x3280

### Support Aircraft
6. **kc135_international.jpg** - International Aerial Refueling
   - Source: https://www.dvidshub.net/image/3816877/international-aerial-refuel
   - VIRIN: 170925-F-QF982-0255
   - Resolution: 4928x3280

### Tactical Bombers
7. **b1_lancer.jpg** - B-1B Lancer Takeoff
   - Source: https://www.dvidshub.net/image/8646233/37th-bomb-squadron-exercise-takeoff
   - VIRIN: 240916-F-DW056-3826
   - Resolution: 6179x3625

## Usage Instructions

1. Download the high-resolution images from the DVIDS URLs above
2. Optimize for web use (compress to ~500KB each while maintaining quality)
3. Rename according to the filenames listed above
4. Place in this directory

## Copyright Notice

All images are public domain works of the United States Air Force, available through the Defense Visual Information Distribution Service (DVIDS). No copyright restrictions apply.

## Image Processing

### Automated Optimization
Use the provided optimization scripts for best results:

```bash
# For DVIDS images (recommended)
python download_usaf_images.py --optimize

# For any images
python optimize_any_images.py --folder downloads/
python optimize_any_images.py --single image.jpg --target 500
```

### Manual Processing Guidelines
For optimal web performance:
- Target file size: ~500KB each (for fast loading)
- Resize to maximum 1920px width
- Compress to JPEG quality 80-90%
- Maintain aspect ratio
- Remove any watermarks (DVIDS images are clean)

### Watermark Removal
🚨 **IMPORTANT**: Use only authentic USAF images from DVIDS
- DVIDS images are PUBLIC DOMAIN with NO watermarks
- Do NOT use Getty Images (commercial, watermarked)
- If you have watermarked images, the optimization script includes basic removal
- For best results, source images directly from DVIDS