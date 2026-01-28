#!/usr/bin/env python
"""
Test the uploaded image in 'test image' folder
"""

from transformers import pipeline
from PIL import Image
from pathlib import Path
from disease_utils import extract_disease_name, get_crop_and_disease, format_disease_output

# Load the model
print("=" * 80)
print("TESTING YOUR UPLOADED IMAGE")
print("=" * 80)
print("\n📥 Loading Plant Disease Detection model...")
pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")
print("✅ Model loaded successfully!\n")

# Get the test image
test_folder = Path(r"c:\Users\Rohit\OneDrive\Desktop\ieeee2\test image")
images = list(test_folder.glob("*.jpg")) + list(test_folder.glob("*.JPG")) + list(test_folder.glob("*.png")) + list(test_folder.glob("*.PNG"))

if not images:
    print("❌ No images found in 'test image' folder!")
else:
    for img_path in images:
        print("=" * 80)
        print(f"📷 Testing Image: {img_path.name}")
        print("=" * 80)
        
        # Load and predict
        image = Image.open(img_path)
        print(f"\n📐 Image size: {image.size[0]}x{image.size[1]} pixels")
        print(f"📊 Image mode: {image.mode}\n")
        
        print("🔍 Running prediction...\n")
        predictions = pipe(image)
        
        # Display results
        print("🎯 PREDICTION RESULTS:")
        print("-" * 80)
        
        # Top prediction (highlighted)
        top = predictions[0]
        formatted = format_disease_output(top['label'], top['score'])
        
        print(f"\n✨ TOP PREDICTION: {top['label']}")
        print(f"   Confidence: {top['score']:.2%}")
        confidence_bar = "█" * int(top['score'] * 50)
        print(f"   [{confidence_bar}]")
        
        # Extract disease name only
        print(f"\n📋 EXTRACTED INFO:")
        print(f"   Crop: {formatted['crop']}")
        print(f"   Disease: {formatted['disease']}")
        print(f"   Confidence Level: {formatted['confidence_level']}")
        
        # All top 10 predictions
        print(f"\n📊 All Top Predictions:")
        print("-" * 80)
        for i, pred in enumerate(predictions[:10], 1):
            bar = "█" * int(pred['score'] * 40)
            marker = "👉" if i == 1 else f"{i:2d}."
            print(f"{marker} {pred['label']:<45} {pred['score']:>6.2%} {bar}")
        
        print("\n" + "=" * 80)

print("\n✨ Testing complete!")
