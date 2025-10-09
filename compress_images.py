#!/usr/bin/env python3
import os
import sys
from PIL import Image
import glob

def get_file_size(filepath):
    """Get file size in bytes"""
    return os.path.getsize(filepath)

def get_total_size(directory):
    """Get total size of all PNG files in directory"""
    total = 0
    for filepath in glob.glob(os.path.join(directory, "*.png")):
        total += get_file_size(filepath)
    return total

def compress_image(input_path, output_path, quality=85, max_width=1200):
    """Compress an image with given quality and max width"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if width is too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error compressing {input_path}: {e}")
        return False

def main():
    img_dir = "img"
    compressed_dir = "img_compressed"
    
    # Create compressed directory
    os.makedirs(compressed_dir, exist_ok=True)
    
    # Get all PNG files
    png_files = glob.glob(os.path.join(img_dir, "*.png"))
    
    print(f"Found {len(png_files)} PNG files")
    
    # Calculate original total size
    original_size = get_total_size(img_dir)
    print(f"Original total size: {original_size / (1024*1024):.2f} MB")
    
    target_size = 1024 * 1024  # 1MB in bytes
    current_size = 0
    
    # First pass: try moderate compression
    compressed_files = []
    for png_file in png_files:
        basename = os.path.basename(png_file)
        output_path = os.path.join(compressed_dir, basename.replace('.png', '.jpg'))
        
        if compress_image(png_file, output_path, quality=75, max_width=1000):
            compressed_files.append(output_path)
            current_size += get_file_size(output_path)
    
    print(f"After first compression: {current_size / (1024*1024):.2f} MB")
    
    # If still too large, apply more aggressive compression
    if current_size > target_size:
        print("Applying more aggressive compression...")
        current_size = 0
        
        for i, png_file in enumerate(png_files):
            basename = os.path.basename(png_file)
            output_path = os.path.join(compressed_dir, basename.replace('.png', '.jpg'))
            
            # Calculate target size for each image (distribute evenly)
            target_per_image = target_size / len(png_files)
            
            # Start with aggressive compression
            quality = 50
            max_width = 800
            
            compress_image(png_file, output_path, quality=quality, max_width=max_width)
            
            # If still too large, reduce further
            while get_file_size(output_path) > target_per_image and quality > 20:
                quality -= 10
                max_width = max(400, max_width - 100)
                compress_image(png_file, output_path, quality=quality, max_width=max_width)
            
            current_size += get_file_size(output_path)
    
    final_size = get_total_size(compressed_dir)
    print(f"Final compressed size: {final_size / (1024*1024):.2f} MB")
    
    if final_size <= target_size:
        print("✅ Successfully compressed to under 1MB!")
        
        # Create backup of original and replace
        os.rename(img_dir, "img_original")
        os.rename(compressed_dir, img_dir)
        print("Original images backed up to 'img_original' folder")
    else:
        print(f"❌ Could not compress to under 1MB. Final size: {final_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()