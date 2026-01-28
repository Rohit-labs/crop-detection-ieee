#!/usr/bin/env python
"""
Complete Plant Disease Detection and Solution System
Integrates ML model prediction with treatment solutions
"""

import json
import subprocess
from pathlib import Path
from transformers import pipeline
from PIL import Image
from disease_utils import extract_disease_name, format_disease_output

def get_solution_from_js(disease_label):
    """
    Call the JavaScript getSolution function and return the result
    
    Args:
        disease_label: The disease label to get solution for
    
    Returns:
        dict: Solution information
    """
    # Create a temporary JS script to get the solution
    js_code = f"""
const {{ getSolution }} = require('./disease_solutions.js');
const solution = getSolution('{disease_label}');
console.log(JSON.stringify(solution, null, 2));
"""
    
    try:
        # Write temporary JS file
        temp_file = Path("temp_get_solution.js")
        temp_file.write_text(js_code)
        
        # Run Node.js to get solution
        result = subprocess.run(
            ['node', str(temp_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Clean up
        temp_file.unlink()
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return None
    except Exception as e:
        print(f"Note: Could not load JS solutions (requires Node.js): {e}")
        return None


def detect_disease(image_path):
    """
    Detect disease from plant image
    
    Args:
        image_path: Path to the image file
    
    Returns:
        dict: Detection results with disease name and confidence
    """
    print("🔍 Loading AI model...")
    pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")
    
    print(f"📷 Analyzing image: {Path(image_path).name}")
    image = Image.open(image_path)
    predictions = pipe(image)
    
    # Get top prediction
    top_prediction = predictions[0]
    disease_info = format_disease_output(top_prediction['label'], top_prediction['score'])
    
    return {
        'full_label': top_prediction['label'],
        'disease_name': disease_info['disease'],
        'crop': disease_info['crop'],
        'confidence': disease_info['confidence'],
        'confidence_level': disease_info['confidence_level'],
        'all_predictions': predictions[:5]
    }


def print_solution(solution):
    """Pretty print the solution"""
    if not solution:
        print("❌ No solution available")
        return
    
    print("\n" + "=" * 80)
    print("💊 TREATMENT & PREVENTION SOLUTIONS")
    print("=" * 80)
    
    print(f"\n🌱 Crop: {solution.get('crop', 'N/A')}")
    print(f"🦠 Disease: {solution.get('disease', 'N/A')}")
    print(f"⚠️  Severity: {solution.get('severity', 'N/A')}")
    
    if 'message' in solution:
        print(f"\n📢 {solution['message']}")
    
    # Healthy plant maintenance
    if 'maintenance' in solution:
        print(f"\n✅ Maintenance Tips:")
        for tip in solution['maintenance']:
            print(f"   • {tip}")
    
    # Disease treatment for India
    if 'india' in solution:
        india_info = solution['india']
        
        if 'organic' in india_info:
            print(f"\n🌿 Organic/Natural Treatment:")
            for treatment in india_info['organic']:
                print(f"   • {treatment}")
        
        if 'chemical' in india_info:
            print(f"\n💊 Chemical Treatment:")
            for treatment in india_info['chemical']:
                print(f"   • {treatment}")
        
        if 'prevention' in india_info:
            print(f"\n🛡️  Prevention Measures:")
            for prevention in india_info['prevention']:
                print(f"   • {prevention}")
    
    # Unknown disease recommendations
    if 'recommendation' in solution:
        print(f"\n💡 Recommendation: {solution['recommendation']}")
    
    if 'general_advice' in solution:
        advice = solution['general_advice']
        
        if 'immediate_actions' in advice:
            print(f"\n⚡ Immediate Actions:")
            for action in advice['immediate_actions']:
                print(f"   • {action}")
        
        if 'contact' in advice:
            print(f"\n📞 Contact for Expert Help:")
            for contact in advice['contact']:
                print(f"   • {contact}")


def analyze_and_treat(image_path):
    """
    Complete workflow: detect disease and provide treatment
    
    Args:
        image_path: Path to plant image
    """
    print("=" * 80)
    print("🌿 PLANT DISEASE DETECTION & TREATMENT SYSTEM")
    print("=" * 80)
    print()
    
    # Step 1: Detect disease
    detection = detect_disease(image_path)
    
    # Step 2: Display detection results
    print("\n" + "=" * 80)
    print("🎯 DETECTION RESULTS")
    print("=" * 80)
    print(f"\n✅ Detected: {detection['full_label']}")
    print(f"🌱 Crop: {detection['crop']}")
    print(f"🦠 Disease: {detection['disease_name']}")
    print(f"📊 Confidence: {detection['confidence']:.2f}% ({detection['confidence_level']})")
    
    print(f"\n📋 Top 5 Predictions:")
    for i, pred in enumerate(detection['all_predictions'], 1):
        bar = "█" * int(pred['score'] * 30)
        print(f"   {i}. {pred['label']:<45} {pred['score']:.2%} {bar}")
    
    # Step 3: Get and display solution
    solution = get_solution_from_js(detection['full_label'])
    
    if solution:
        print_solution(solution)
    else:
        print("\n📝 Note: Install Node.js to access treatment solutions database")
        print("   For now, showing detection results only.")
    
    print("\n" + "=" * 80)
    
    return {
        'detection': detection,
        'solution': solution
    }


if __name__ == "__main__":
    # Test with image from 'test image' folder
    test_folder = Path(r"c:\Users\Rohit\OneDrive\Desktop\ieeee2\test image")
    images = list(test_folder.glob("*.jpg")) + list(test_folder.glob("*.JPG")) + \
             list(test_folder.glob("*.png")) + list(test_folder.glob("*.PNG"))
    
    if images:
        for img_path in images:
            result = analyze_and_treat(str(img_path))
            print("\n✨ Analysis complete!\n")
            
            # Also save result to JSON
            output_file = Path("detection_result.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to: {output_file}")
    else:
        print("❌ No images found in 'test image' folder!")
        print("   Please add an image to test.")
