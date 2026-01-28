from transformers import pipeline
from PIL import Image
from pathlib import Path

# Quick test to see exact model output
pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")

test_folder = Path(r"c:\Users\Rohit\OneDrive\Desktop\ieeee2\test image")
images = list(test_folder.glob("*.jpg")) + list(test_folder.glob("*.JPG"))

if images:
    image = Image.open(images[0])
    predictions = pipe(image)
    
    print("Top 3 predictions - EXACT output:")
    for i, pred in enumerate(predictions[:3], 1):
        print(f"{i}. Label: '{pred['label']}'")
        print(f"   Type: {type(pred['label'])}")
        print(f"   Contains '___': {'___' in pred['label']}")
        print(f"   Repr: {repr(pred['label'])}")
        print()
