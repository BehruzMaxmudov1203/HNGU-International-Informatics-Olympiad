from PIL import Image
import os
import glob
import sys

def get_color_shades(image_path):
    """Extract unique colors from an image"""
    print(f"Loading virus sample: {image_path}")
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = list(img.getdata())
    unique_colors = set(pixels)
    print(f"Found {len(unique_colors)} unique color shades in virus.bmp")
    
    # Show the actual colors for verification
    if len(unique_colors) <= 20:
        print("Color shades (RGB values):")
        for i, color in enumerate(sorted(unique_colors), 1):
            print(f"  {i}. RGB{color}")
    
    return unique_colors

def check_image_for_shades(image_path, virus_shades, threshold=0.5):
    """Check if an image contains at least threshold% of virus color shades"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = set(img.getdata())
        
        # Count how many virus shades are present in this image
        matching_shades = pixels.intersection(virus_shades)
        
        # Calculate percentage
        if len(virus_shades) == 0:
            return False, 0.0
        
        percentage = (len(matching_shades) / len(virus_shades)) * 100
        return percentage >= threshold, percentage
    except Exception as e:
        print(f"  Error processing {os.path.basename(image_path)}: {e}")
        return False, 0.0

def main():
    print("="*70)
    print("Virus Detection in Soil Layer Images")
    print("="*70)
    
    # Path to Scan folder
    scan_folder = r"c:\Users\Behruz\Desktop\Turk_man\Scan-20260415"
    
    if not os.path.exists(scan_folder):
        print(f"ERROR: Scan folder not found at {scan_folder}")
        return
    
    # Find virus.bmp
    virus_path = os.path.join(scan_folder, "virus.bmp")
    
    if not os.path.exists(virus_path):
        print(f"\nERROR: virus.bmp not found in {scan_folder}")
        print("\nThe task requires virus.bmp file which contains the reference")
        print("color shades for the virus detection.")
        print("\nPlease:")
        print("1. Download virus.bmp from your Moodle course")
        print("2. Place it in: " + scan_folder)
        print("3. Run this script again")
        return
    
    print(f"\n✓ Found virus.bmp")
    
    # Get virus color shades
    virus_shades = get_color_shades(virus_path)
    
    if len(virus_shades) == 0:
        print("ERROR: No color shades found in virus.bmp")
        return
    
    if len(virus_shades) > 10:
        print(f"WARNING: Found {len(virus_shades)} shades (expected up to 10)")
    
    print(f"\nScanning all BMP images in {scan_folder}...")
    print("-" * 70)
    
    # Count files that match criteria
    matching_files_count = 0
    total_files = 0
    
    # Get all BMP files in Scan folder (excluding virus.bmp)
    bmp_files = glob.glob(os.path.join(scan_folder, "*.bmp"))
    bmp_files = [f for f in bmp_files if os.path.basename(f).lower() != "virus.bmp"]
    bmp_files.sort()  # Sort for consistent order
    
    print(f"Total BMP files to scan: {len(bmp_files)}")
    print(f"Threshold: >= 0.5% of virus color shades")
    print("-" * 70)
    
    # Process each file
    for bmp_file in bmp_files:
        total_files += 1
        matches, percentage = check_image_for_shades(bmp_file, virus_shades, 0.5)
        
        if matches:
            matching_files_count += 1
            if matching_files_count <= 20:  # Show first 20 matches
                print(f"✓ {os.path.basename(bmp_file):20} - {percentage:.2f}% match")
    
    print("-" * 70)
    print(f"\nNATIJALAR:")
    print(f"  Jami tekshirilgan fayllar: {total_files}")
    print(f"  Virus aniqlangan fayllar (>= 0.5%): {matching_files_count}")
    print("="*70)
    print(f"\n>>> JAVOB: {matching_files_count} <<<")
    print("="*70)
    print(f"\nEnter this number in the Moodle portal answer field.")
    
if __name__ == "__main__":
    main()


