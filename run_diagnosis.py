#!/usr/bin/env python
"""
All-in-One Plant Disease Detection and Treatment System
Detects disease and provides treatment solutions in one go
"""

from transformers import pipeline
from PIL import Image
from pathlib import Path
from disease_utils import format_disease_output

# Disease Solutions Database (Python version)
DISEASE_SOLUTIONS = {
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "severity": "Medium",
        "organic": [
            "Neem oil spray (3 ml/L water)",
            "Remove and destroy infected leaves immediately",
            "Spray with Trichoderma viride (5-10 g/L)",
            "Apply Bordeaux mixture (1%)"
        ],
        "chemical": [
            "Mancozeb 75% WP (2 g/L water)",
            "Chlorothalonil 75% WP (2 g/L)",
            "Azoxystrobin 23% SC (1 ml/L)"
        ],
        "prevention": [
            "Avoid overhead irrigation",
            "Ensure proper plant spacing for air circulation",
            "Crop rotation with non-solanaceous crops",
            "Mulching to prevent soil splash"
        ]
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "severity": "High",
        "organic": [
            "Copper oxychloride spray (3 g/L)",
            "Bordeaux mixture (1%) spray",
            "Remove infected plants immediately"
        ],
        "chemical": [
            "Mancozeb 75% WP (2.5 g/L)",
            "Cymoxanil + Mancozeb (2 g/L)",
            "Metalaxyl 8% + Mancozeb 64% WP (2.5 g/L)"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Avoid wet foliage - irrigate in morning",
            "Ensure proper drainage",
            "Destroy volunteer plants and crop residue"
        ]
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "severity": "Medium",
        "organic": [
            "Copper-based bactericides (2-3 g/L)",
            "Remove infected plant parts",
            "Neem oil spray"
        ],
        "chemical": [
            "Streptocycline 90% + Copper oxychloride 50% (0.3 g/L)",
            "Copper hydroxide (2 g/L)"
        ],
        "prevention": [
            "Use certified disease-free seeds",
            "Avoid overhead irrigation",
            "Crop rotation for 2-3 years"
        ]
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "severity": "Medium",
        "organic": [
            "Neem oil spray (3 ml/L)",
            "Copper-based fungicides",
            "Remove infected foliage"
        ],
        "chemical": [
            "Mancozeb 75% WP (2.5 g/L)",
            "Chlorothalonil 75% WP (2 g/L)",
            "Azoxystrobin 23% SC (1 ml/L)"
        ],
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Crop rotation (3-4 years)",
            "Hill up soil around plants"
        ]
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "severity": "Very High",
        "organic": [
            "Copper oxychloride (3 g/L) - preventive",
            "Destroy infected plants immediately"
        ],
        "chemical": [
            "Mancozeb 75% WP (2.5 g/L)",
            "Metalaxyl + Mancozeb (2.5 g/L)",
            "Cymoxanil + Mancozeb (2 g/L)"
        ],
        "prevention": [
            "Plant certified disease-free tubers",
            "Early planting to avoid monsoon",
            "Monitor weather for disease-favorable conditions"
        ]
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot",
        "severity": "High",
        "organic": [
            "Prune out infected branches",
            "Remove mummified fruits",
            "Copper-based fungicides"
        ],
        "chemical": [
            "Mancozeb 75% WP (2.5 g/L)",
            "Captan 50% WP (2 g/L)",
            "Thiophanate-methyl 70% WP (1 g/L)"
        ],
        "prevention": [
            "Remove all mummies and cankers",
            "Prune dead wood",
            "Maintain tree vigor with proper nutrition"
        ]
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot",
        "severity": "Medium",
        "organic": [
            "Copper-based bactericides (2 g/L)",
            "Remove and destroy infected plants",
            "Neem oil spray"
        ],
        "chemical": [
            "Streptocycline + Copper oxychloride (0.3 g/L)",
            "Copper hydroxide (2 g/L)"
        ],
        "prevention": [
            "Use certified pathogen-free seeds",
            "Avoid working with wet plants",
            "2-3 year crop rotation"
        ]
    },
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Black Rot",
        "severity": "High",
        "organic": [
            "Remove infected berries and leaves",
            "Copper-based fungicides",
            "Bordeaux mixture spray"
        ],
        "chemical": [
            "Mancozeb 75% WP (2.5 g/L)",
            "Captan 50% WP (2 g/L)",
            "Azoxystrobin 23% SC (1 ml/L)"
        ],
        "prevention": [
            "Remove mummified berries",
            "Prune for air circulation",
            "Apply fungicides from bud break to harvest"
        ]
    }
}

# Healthy plant responses
HEALTHY_RESPONSES = {
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "message": "Your tomato plant appears healthy! Keep up the good practices.",
        "maintenance": [
            "Continue regular watering (avoid wetting leaves)",
            "Maintain balanced fertilization",
            "Monitor for early signs of pests or diseases",
            "Prune suckers for better air circulation"
        ]
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "message": "Your potato plant is healthy!",
        "maintenance": [
            "Continue proper hilling",
            "Maintain consistent soil moisture",
            "Monitor for Colorado potato beetles",
            "Apply balanced NPK fertilizer"
        ]
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy",
        "message": "Your apple tree appears healthy!",
        "maintenance": [
            "Continue annual pruning",
            "Monitor for pest activity",
            "Apply dormant oil spray in spring",
            "Remove fallen fruit and leaves"
        ]
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy",
        "message": "Your bell pepper plant is healthy!",
        "maintenance": [
            "Continue consistent watering",
            "Apply balanced fertilizer",
            "Monitor for aphids and other pests",
            "Mulch to maintain soil moisture"
        ]
    }
}


def get_solution(disease_label):
    """Get treatment solution for detected disease"""
    # Normalize the label - convert from model format to database format
    # Model returns: "Tomato Bacterial spot" 
    # Database needs: "Tomato___Bacterial_spot"
    
    normalized_label = disease_label.strip()
    
    # Replace spaces with underscores and then convert single crop-disease separator to triple underscore
    # First, let's try to find a match by replacing space with ___
    if " " in normalized_label:
        # For labels like "Tomato Bacterial spot" -> "Tomato___Bacterial_spot"
        parts = normalized_label.split(" ", 1)  # Split only on first space
        if len(parts) == 2:
            crop = parts[0]
            disease = parts[1].replace(" ", "_")  # Replace remaining spaces with single underscore
            normalized_label = f"{crop}___{disease}"
    
    # Check if healthy
    if "healthy" in normalized_label.lower():
        # Try to find exact match first
        for key in HEALTHY_RESPONSES.keys():
            if normalized_label == key or disease_label in key or key in normalized_label:
                return HEALTHY_RESPONSES[key]
        
        return {
            "crop": normalized_label.split("___")[0] if "___" in normalized_label else "Plant",
            "disease": "Healthy",
            "message": "Your plant appears healthy!",
            "maintenance": ["Continue good agricultural practices"]
        }
    
    # Check if solution exists with normalized label
    if normalized_label in DISEASE_SOLUTIONS:
        return DISEASE_SOLUTIONS[normalized_label]
    
    # Try original label as fallback
    if disease_label in DISEASE_SOLUTIONS:
        return DISEASE_SOLUTIONS[disease_label]
    
    # Unknown disease
    parts = disease_label.split(" ", 1) if " " in disease_label else [disease_label]
    return {
        "crop": parts[0] if len(parts) > 0 else "Unknown",
        "disease": parts[1] if len(parts) > 1 else disease_label,
        "message": f"No specific solution available for this disease.",
        "recommendation": "Please consult with a local agricultural extension officer or plant pathologist."
    }


def analyze_plant_disease(image_path):
    """
    Complete analysis: Detect disease and provide treatment
    """
    print("=" * 80)
    print("🌿 PLANT DISEASE DETECTION & TREATMENT SYSTEM")
    print("=" * 80)
    
    # Load model
    print("\n📥 Loading AI model...")
    pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")
    print("✅ Model loaded!\n")
    
    # Analyze image
    print(f"📷 Analyzing: {Path(image_path).name}")
    image = Image.open(image_path)
    predictions = pipe(image)
    
    # Get top prediction
    top = predictions[0]
    result = format_disease_output(top['label'], top['score'])
    
    # Display detection results
    print("\n" + "=" * 80)
    print("🎯 DETECTION RESULTS")
    print("=" * 80)
    print(f"\n🌱 Crop:       {result['crop']}")
    print(f"🦠 Disease:    {result['disease']}")
    print(f"📊 Confidence: {result['confidence']:.2f}% ({result['confidence_level']})")
    
    confidence_bar = "█" * int(top['score'] * 50)
    print(f"   [{confidence_bar}]")
    
    # Get treatment solution
    solution = get_solution(top['label'])
    
    # Display solution
    print("\n" + "=" * 80)
    print("💊 TREATMENT & PREVENTION")
    print("=" * 80)
    
    if 'message' in solution:
        print(f"\n📢 {solution['message']}")
    
    print(f"\n⚠️  Severity: {solution.get('severity', 'N/A')}")
    
    # Healthy plant maintenance
    if 'maintenance' in solution:
        print(f"\n✅ Maintenance Tips:")
        for tip in solution['maintenance']:
            print(f"   • {tip}")
    
    # Disease treatments
    if 'organic' in solution:
        print(f"\n🌿 Organic/Natural Treatment:")
        for treatment in solution['organic']:
            print(f"   • {treatment}")
    
    if 'chemical' in solution:
        print(f"\n💊 Chemical Treatment:")
        for treatment in solution['chemical']:
            print(f"   • {treatment}")
    
    if 'prevention' in solution:
        print(f"\n🛡️  Prevention Measures:")
        for prevention in solution['prevention']:
            print(f"   • {prevention}")
    
    if 'recommendation' in solution:
        print(f"\n💡 {solution['recommendation']}")
    
    print("\n" + "=" * 80)
    print("✨ Analysis Complete!")
    print("=" * 80)
    
    return {
        'detection': result,
        'solution': solution
    }


if __name__ == "__main__":
    # Test images from 'test image' folder
    test_folder = Path(r"c:\Users\Rohit\OneDrive\Desktop\ieeee2\test image")
    images = list(test_folder.glob("*.jpg")) + list(test_folder.glob("*.JPG")) + \
             list(test_folder.glob("*.png")) + list(test_folder.glob("*.PNG"))
    
    if images:
        for img_path in images:
            result = analyze_plant_disease(str(img_path))
            print()
    else:
        print("❌ No images found in 'test image' folder!")
        print("   Please add plant images to test.")
