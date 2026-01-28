#!/usr/bin/env python
"""
Utility functions for plant disease detection
"""

def extract_disease_name(prediction_label):
    """
    Extract just the disease name from the prediction label
    
    Args:
        prediction_label: Full prediction label like "Tomato___Early_blight"
    
    Returns:
        str: Just the disease name, e.g., "Early_blight" or "healthy"
    """
    # Split by triple underscore
    parts = prediction_label.split("___")
    
    if len(parts) == 2:
        # Format: "Crop___Disease"
        disease = parts[1]
        return disease
    else:
        # If no triple underscore, return as is
        return prediction_label


def get_crop_and_disease(prediction_label):
    """
    Extract crop and disease separately
    
    Args:
        prediction_label: Full prediction label like "Tomato___Early_blight"
    
    Returns:
        dict: {"crop": "Tomato", "disease": "Early_blight"}
    """
    parts = prediction_label.split("___")
    
    if len(parts) == 2:
        return {
            "crop": parts[0],
            "disease": parts[1]
        }
    else:
        return {
            "crop": "Unknown",
            "disease": prediction_label
        }


def format_disease_output(prediction_label, confidence):
    """
    Format the disease detection output in a clean way
    
    Args:
        prediction_label: Full prediction label
        confidence: Confidence score (0-1)
    
    Returns:
        dict: Formatted output with crop, disease, and confidence
    """
    info = get_crop_and_disease(prediction_label)
    
    return {
        "full_label": prediction_label,
        "crop": info["crop"],
        "disease": info["disease"],
        "confidence": round(confidence * 100, 2),
        "confidence_level": get_confidence_level(confidence)
    }


def get_confidence_level(confidence):
    """
    Categorize confidence level
    
    Args:
        confidence: Confidence score (0-1)
    
    Returns:
        str: Confidence level category
    """
    if confidence >= 0.9:
        return "Very High"
    elif confidence >= 0.75:
        return "High"
    elif confidence >= 0.5:
        return "Medium"
    else:
        return "Low"


def normalize_disease_label(label):
    """
    Normalize disease label to match database format
    Converts 'Tomato Bacterial spot' to 'Tomato___Bacterial_spot'
    
    Args:
        label: Raw label from model (e.g., "Tomato Bacterial spot")
    
    Returns:
        str: Normalized label (e.g., "Tomato___Bacterial_spot")
    """
    label = label.strip()
    
    # If already has triple underscores, return as is
    if "___" in label:
        return label
    
    # Split on first space to separate crop from disease
    if " " in label:
        parts = label.split(" ", 1)
        if len(parts) == 2:
            crop = parts[0]
            disease = parts[1].replace(" ", "_")
            return f"{crop}___{disease}"
    
    return label


if __name__ == "__main__":
    # Test the functions
    test_labels = [
        "Tomato___Early_blight",
        "Apple___Black_rot",
        "Pepper,_bell___Bacterial_spot",
        "Potato___healthy"
    ]
    
    print("Testing disease extraction functions:\n")
    
    for label in test_labels:
        print(f"Original: {label}")
        print(f"Disease only: {extract_disease_name(label)}")
        print(f"Separated: {get_crop_and_disease(label)}")
        print(f"Formatted: {format_disease_output(label, 0.95)}")
        print("-" * 60)
