#!/usr/bin/env python
"""
Test the Plant Disease Detection model on images from the archive dataset
"""

import os
import random
from pathlib import Path
from transformers import pipeline
from PIL import Image
import time

def normalize_label(label):
    """Normalize label for comparison"""
    return label.lower().replace("_", " ").replace(",", "").strip()

def test_model_on_dataset(dataset_path, num_samples_per_class=3, show_top_k=5):
    """
    Test the model on random samples from the dataset
    
    Args:
        dataset_path: Path to the dataset folder
        num_samples_per_class: Number of random samples to test per class
        show_top_k: Number of top predictions to show
    """
    print("=" * 80)
    print("PLANT DISEASE DETECTION MODEL TEST")
    print("=" * 80)
    
    # Load the model
    print("\n📥 Loading model: Diginsa/Plant-Disease-Detection-Project")
    print("Please wait...\n")
    pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")
    print("✅ Model loaded successfully!\n")
    
    # Get all class folders
    train_path = Path(dataset_path) / "PlantVillage" / "train"
    class_folders = [f for f in train_path.iterdir() if f.is_dir()]
    
    print(f"📊 Found {len(class_folders)} disease classes in dataset\n")
    print("=" * 80)
    
    # Statistics
    total_tests = 0
    correct_predictions = 0
    results = []
    
    # Test random samples from each class
    for class_folder in sorted(class_folders):
        class_name = class_folder.name
        
        # Get all images in this class
        image_files = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png")) + list(class_folder.glob("*.JPG"))
        
        if not image_files:
            continue
        
        # Select random samples
        num_samples = min(num_samples_per_class, len(image_files))
        selected_images = random.sample(image_files, num_samples)
        
        print(f"\n🔍 Testing class: {class_name}")
        print(f"   Total images: {len(image_files)} | Testing: {num_samples} samples")
        print("-" * 80)
        
        for img_path in selected_images:
            try:
                # Load and predict
                image = Image.open(img_path)
                start_time = time.time()
                predictions = pipe(image)
                inference_time = time.time() - start_time
                
                # Get top prediction
                top_prediction = predictions[0]
                predicted_label = top_prediction['label']
                confidence = top_prediction['score']
                
                # Check if prediction is correct (fuzzy matching)
                true_label_norm = normalize_label(class_name)
                pred_label_norm = normalize_label(predicted_label)
                
                is_correct = pred_label_norm in true_label_norm or true_label_norm in pred_label_norm
                
                total_tests += 1
                if is_correct:
                    correct_predictions += 1
                
                # Display result
                status = "✅ CORRECT" if is_correct else "❌ WRONG"
                print(f"\n   Image: {img_path.name}")
                print(f"   True Label:      {class_name}")
                print(f"   Predicted:       {predicted_label} ({confidence:.2%}) {status}")
                print(f"   Inference Time:  {inference_time:.3f}s")
                
                # Show top predictions if wrong
                if not is_correct and show_top_k > 1:
                    print(f"   Top {show_top_k} predictions:")
                    for i, pred in enumerate(predictions[:show_top_k], 1):
                        print(f"      {i}. {pred['label']}: {pred['score']:.2%}")
                
                results.append({
                    'true_label': class_name,
                    'predicted_label': predicted_label,
                    'confidence': confidence,
                    'correct': is_correct,
                    'inference_time': inference_time
                })
                
            except Exception as e:
                print(f"   ⚠️  Error processing {img_path.name}: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if total_tests > 0:
        accuracy = (correct_predictions / total_tests) * 100
        avg_inference_time = sum(r['inference_time'] for r in results) / len(results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\n📈 Total Tests:         {total_tests}")
        print(f"✅ Correct Predictions: {correct_predictions}")
        print(f"❌ Wrong Predictions:   {total_tests - correct_predictions}")
        print(f"🎯 Accuracy:            {accuracy:.2f}%")
        print(f"⚡ Avg Inference Time:  {avg_inference_time:.3f}s")
        print(f"📊 Avg Confidence:      {avg_confidence:.2%}")
        
        # Show some wrong predictions
        wrong_predictions = [r for r in results if not r['correct']]
        if wrong_predictions:
            print(f"\n❌ Examples of misclassifications:")
            for r in wrong_predictions[:5]:
                print(f"   True: {r['true_label']}")
                print(f"   Predicted: {r['predicted_label']} ({r['confidence']:.2%})")
                print()
    else:
        print("\n⚠️  No images were tested!")
    
    print("=" * 80)
    return results

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Path to your dataset
    dataset_path = r"c:\Users\Rohit\OneDrive\Desktop\ieeee2\archive"
    
    # Run the test
    # Adjust num_samples_per_class to test more or fewer images
    results = test_model_on_dataset(
        dataset_path=dataset_path,
        num_samples_per_class=2,  # Test 2 random images per class
        show_top_k=5  # Show top 5 predictions for wrong predictions
    )
    
    print("\n🎉 Testing complete!")
