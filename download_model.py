#!/usr/bin/env python
"""
Download and use the Plant Disease Detection pretrained model
from Hugging Face
"""

from transformers import pipeline

print("Loading the pretrained model: Diginsa/Plant-Disease-Detection-Project")
print("This may take a few moments on first run as it downloads the model...\n")

# Use a pipeline as a high-level helper
pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")

print("Model loaded successfully!")
print("\nRunning inference on test image...")

# Run inference on an image
result = pipe("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/parrots.png")

print("\nInference Results:")
for prediction in result:
    print(f"  - {prediction['label']}: {prediction['score']:.4f}")

print("\nModel download complete and working!")
