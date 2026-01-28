#!/usr/bin/env python
"""
Plant Disease Detection REST API
Provides endpoints for React Native app integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from PIL import Image
import io
import base64
from disease_utils import normalize_disease_label

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native app

# Load model once at startup
print("🔄 Loading AI model...")
pipe = pipeline("image-classification", model="Diginsa/Plant-Disease-Detection-Project")
print("✅ Model loaded successfully!\n")

# Complete disease solutions database
DISEASE_SOLUTIONS = {
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "severity": "Medium",
        "india": {
            "organic": [
                "Neem oil spray (3 ml/L water)",
                "Remove and destroy infected leaves immediately",
                "Spray with Trichoderma viride (5-10 g/L)",
                "Apply Bordeaux mixture (1%)",
                "Use copper-based fungicides"
            ],
            "chemical": [
                "Mancozeb 75% WP (2 g/L water)",
                "Chlorothalonil 75% WP (2 g/L)",
                "Azoxystrobin 23% SC (1 ml/L)",
                "Difenoconazole 25% EC (0.5 ml/L)"
            ],
            "prevention": [
                "Avoid overhead irrigation",
                "Ensure proper plant spacing for air circulation",
                "Crop rotation with non-solanaceous crops",
                "Mulching to prevent soil splash",
                "Remove plant debris after harvest"
            ]
        }
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "severity": "High",
        "india": {
            "organic": [
                "Copper oxychloride spray (3 g/L)",
                "Bordeaux mixture (1%) spray",
                "Remove infected plants immediately",
                "Use resistant varieties"
            ],
            "chemical": [
                "Mancozeb 75% WP (2.5 g/L)",
                "Cymoxanil + Mancozeb (2 g/L)",
                "Metalaxyl 8% + Mancozeb 64% WP (2.5 g/L)",
                "Dimethomorph 50% WP (1 g/L)"
            ],
            "prevention": [
                "Plant resistant varieties",
                "Avoid wet foliage - irrigate in morning",
                "Ensure proper drainage",
                "Wide plant spacing",
                "Destroy volunteer plants and crop residue"
            ]
        }
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "severity": "Medium",
        "india": {
            "organic": [
                "Copper-based bactericides (2-3 g/L)",
                "Remove infected plant parts",
                "Use disease-free seeds",
                "Neem oil spray"
            ],
            "chemical": [
                "Streptocycline 90% + Copper oxychloride 50% (0.3 g/L)",
                "Copper hydroxide (2 g/L)",
                "Kasugamycin 3% SL (2 ml/L)"
            ],
            "prevention": [
                "Use certified disease-free seeds",
                "Avoid overhead irrigation",
                "Sanitize tools between plants",
                "Crop rotation for 2-3 years",
                "Remove weeds that harbor bacteria"
            ]
        }
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "severity": "Medium",
        "india": {
            "organic": [
                "Improve air circulation",
                "Remove infected leaves",
                "Baking soda spray (5 g/L + few drops soap)",
                "Neem oil application"
            ],
            "chemical": [
                "Chlorothalonil 75% WP (2 g/L)",
                "Mancozeb 75% WP (2 g/L)",
                "Azoxystrobin 23% SC (1 ml/L)"
            ],
            "prevention": [
                "Ensure good ventilation in greenhouse",
                "Reduce humidity levels",
                "Avoid overhead watering",
                "Use resistant varieties",
                "Proper plant spacing"
            ]
        }
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "severity": "Medium",
        "india": {
            "organic": [
                "Copper-based fungicide spray",
                "Remove infected lower leaves",
                "Compost tea spray",
                "Neem oil application"
            ],
            "chemical": [
                "Mancozeb 75% WP (2 g/L)",
                "Chlorothalonil 75% WP (2 g/L)",
                "Azoxystrobin + Difenoconazole (1 ml/L)"
            ],
            "prevention": [
                "Mulch around plants",
                "Water at base of plants only",
                "Stake plants for air circulation",
                "3-year crop rotation",
                "Remove plant debris"
            ]
        }
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "severity": "Medium",
        "india": {
            "organic": [
                "Neem oil spray (3 ml/L)",
                "Copper-based fungicides",
                "Remove infected foliage",
                "Trichoderma application to soil"
            ],
            "chemical": [
                "Mancozeb 75% WP (2.5 g/L)",
                "Chlorothalonil 75% WP (2 g/L)",
                "Azoxystrobin 23% SC (1 ml/L)",
                "Difenoconazole 25% EC (0.5 ml/L)"
            ],
            "prevention": [
                "Use certified disease-free seed potatoes",
                "Crop rotation (3-4 years)",
                "Hill up soil around plants",
                "Balanced fertilization",
                "Destroy crop residue after harvest"
            ]
        }
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "severity": "Very High",
        "india": {
            "organic": [
                "Copper oxychloride (3 g/L) - preventive",
                "Bordeaux mixture spray",
                "Destroy infected plants immediately",
                "Use resistant varieties"
            ],
            "chemical": [
                "Mancozeb 75% WP (2.5 g/L)",
                "Metalaxyl + Mancozeb (2.5 g/L)",
                "Cymoxanil + Mancozeb (2 g/L)",
                "Dimethomorph + Pyraclostrobin (1.5 ml/L)"
            ],
            "prevention": [
                "Plant certified disease-free tubers",
                "Early planting to avoid monsoon",
                "Earthing up properly",
                "Monitor weather for disease-favorable conditions",
                "Destroy cull piles and volunteers"
            ]
        }
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot",
        "severity": "Medium",
        "india": {
            "organic": [
                "Copper-based bactericides (2 g/L)",
                "Remove and destroy infected plants",
                "Use disease-free seeds and transplants",
                "Neem oil spray"
            ],
            "chemical": [
                "Streptocycline + Copper oxychloride (0.3 g/L)",
                "Copper hydroxide (2 g/L)",
                "Kasugamycin 3% SL (2 ml/L)"
            ],
            "prevention": [
                "Use certified pathogen-free seeds",
                "Avoid working with wet plants",
                "Drip irrigation instead of overhead",
                "2-3 year crop rotation",
                "Sanitize tools and equipment"
            ]
        }
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot",
        "severity": "High",
        "india": {
            "organic": [
                "Prune out infected branches",
                "Remove mummified fruits",
                "Copper-based fungicides",
                "Improve orchard sanitation"
            ],
            "chemical": [
                "Mancozeb 75% WP (2.5 g/L)",
                "Captan 50% WP (2 g/L)",
                "Thiophanate-methyl 70% WP (1 g/L)",
                "Ziram 76% WP (2 g/L)"
            ],
            "prevention": [
                "Remove all mummies and cankers",
                "Prune dead wood",
                "Maintain tree vigor with proper nutrition",
                "Avoid tree stress",
                "Regular monitoring and early treatment"
            ]
        }
    },
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Black Rot",
        "severity": "High",
        "india": {
            "organic": [
                "Remove infected berries and leaves",
                "Copper-based fungicides",
                "Bordeaux mixture spray",
                "Improve air circulation through pruning"
            ],
            "chemical": [
                "Mancozeb 75% WP (2.5 g/L)",
                "Captan 50% WP (2 g/L)",
                "Azoxystrobin 23% SC (1 ml/L)",
                "Myclobutanil 10% WP (0.5 g/L)"
            ],
            "prevention": [
                "Remove mummified berries",
                "Prune for air circulation",
                "Remove infected plant parts promptly",
                "Apply fungicides from bud break to harvest",
                "Clean up fallen debris"
            ]
        }
    }
}

# Healthy plant responses
HEALTHY_RESPONSES = {
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "severity": "None",
        "message": "Your tomato plant appears healthy! Keep up the good practices.",
        "maintenance": [
            "Continue regular watering (avoid wetting leaves)",
            "Maintain balanced fertilization",
            "Monitor for early signs of pests or diseases",
            "Ensure proper plant spacing",
            "Prune suckers for better air circulation"
        ]
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "severity": "None",
        "message": "Your potato plant is healthy!",
        "maintenance": [
            "Continue proper hilling",
            "Maintain consistent soil moisture",
            "Monitor for Colorado potato beetles",
            "Apply balanced NPK fertilizer",
            "Harvest at proper maturity"
        ]
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy",
        "severity": "None",
        "message": "Your apple tree appears healthy!",
        "maintenance": [
            "Continue annual pruning",
            "Monitor for pest activity",
            "Apply dormant oil spray in spring",
            "Maintain proper tree nutrition",
            "Remove fallen fruit and leaves"
        ]
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy",
        "severity": "None",
        "message": "Your bell pepper plant is healthy!",
        "maintenance": [
            "Continue consistent watering",
            "Apply balanced fertilizer",
            "Monitor for aphids and other pests",
            "Mulch to maintain soil moisture",
            "Provide support if needed"
        ]
    }
}


def get_solution(normalized_label):
    """Get treatment solution for detected disease"""
    # Check if healthy
    if "healthy" in normalized_label.lower():
        for key in HEALTHY_RESPONSES.keys():
            if normalized_label == key or normalized_label.lower() in key.lower():
                return HEALTHY_RESPONSES[key]
        
        crop = normalized_label.split("___")[0] if "___" in normalized_label else "Plant"
        return {
            "crop": crop,
            "disease": "Healthy",
            "severity": "None",
            "message": f"Your {crop} plant appears healthy!",
            "maintenance": [
                "Continue regular watering",
                "Monitor for any changes",
                "Maintain proper nutrition"
            ]
        }
    
    # Check if solution exists
    if normalized_label in DISEASE_SOLUTIONS:
        return DISEASE_SOLUTIONS[normalized_label]
    
    # Unknown disease
    parts = normalized_label.split("___")
    crop = parts[0] if len(parts) > 0 else "Unknown"
    disease = parts[1] if len(parts) > 1 else normalized_label
    
    return {
        "crop": crop,
        "disease": disease,
        "severity": "Unknown",
        "message": f"No specific solution available for {disease} in {crop}.",
        "recommendation": "Please consult with a local agricultural extension officer or plant pathologist for proper diagnosis and treatment.",
        "contact": [
            "Nearest Krishi Vigyan Kendra (KVK)",
            "State Agricultural University",
            "ICAR institutes",
            "Local agricultural extension services"
        ]
    }


@app.route('/', methods=['GET'])
def home():
    """API home page"""
    return jsonify({
        "service": "Plant Disease Detection API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health_check": "GET /health",
            "predict_with_file": "POST /predict (multipart/form-data)",
            "predict_with_base64": "POST /predict-base64 (JSON)"
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Plant Disease Detection API is running",
        "model": "Diginsa/Plant-Disease-Detection-Project"
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict disease from uploaded image file
    
    Request: multipart/form-data with 'image' file
    Response: JSON with disease prediction and solutions
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "error": "No image file provided. Please upload an image."
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "Empty filename"
            }), 400
        
        # Read and process image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get predictions from model
        results = pipe(image)
        
        # Get top prediction
        top_prediction = results[0]
        raw_label = top_prediction['label']
        confidence = top_prediction['score']
        
        # Normalize label to match database format
        normalized_label = normalize_disease_label(raw_label)
        
        # Get solution
        solution = get_solution(normalized_label)
        
        # Prepare response
        response = {
            "success": True,
            "prediction": {
                "raw_label": raw_label,
                "normalized_label": normalized_label,
                "confidence": round(confidence * 100, 2),
                "confidence_percentage": f"{round(confidence * 100, 2)}%",
                "crop": solution.get("crop", "Unknown"),
                "disease": solution.get("disease", "Unknown"),
                "severity": solution.get("severity", "Unknown")
            },
            "solution": solution,
            "all_predictions": [
                {
                    "label": pred['label'],
                    "confidence": round(pred['score'] * 100, 2)
                }
                for pred in results[:5]  # Top 5 predictions
            ]
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error processing image: {str(e)}"
        }), 500


@app.route('/predict-base64', methods=['POST'])
def predict_base64():
    """
    Predict disease from base64 encoded image
    
    Request: JSON with 'image' field containing base64 string
    Response: JSON with disease prediction and solutions
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                "success": False,
                "error": "No image data provided. Send JSON with 'image' field."
            }), 400
        
        # Decode base64 image
        image_data = data['image']
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get predictions from model
        results = pipe(image)
        
        # Get top prediction
        top_prediction = results[0]
        raw_label = top_prediction['label']
        confidence = top_prediction['score']
        
        # Normalize label
        normalized_label = normalize_disease_label(raw_label)
        
        # Get solution
        solution = get_solution(normalized_label)
        
        # Prepare response
        response = {
            "success": True,
            "prediction": {
                "raw_label": raw_label,
                "normalized_label": normalized_label,
                "confidence": round(confidence * 100, 2),
                "confidence_percentage": f"{round(confidence * 100, 2)}%",
                "crop": solution.get("crop", "Unknown"),
                "disease": solution.get("disease", "Unknown"),
                "severity": solution.get("severity", "Unknown")
            },
            "solution": solution,
            "all_predictions": [
                {
                    "label": pred['label'],
                    "confidence": round(pred['score'] * 100, 2)
                }
                for pred in results[:5]
            ]
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error processing image: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌿 PLANT DISEASE DETECTION API SERVER")
    print("=" * 60)
    print("\n📡 API Endpoints:")
    print("   GET  /          - API information")
    print("   GET  /health    - Health check")
    print("   POST /predict   - Upload image file (multipart/form-data)")
    print("   POST /predict-base64 - Send base64 image (JSON)")
    print("\n🌐 Server starting on: http://0.0.0.0:5000")
    print("💡 Access from other devices using your IP address")
    print("=" * 60 + "\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True)
