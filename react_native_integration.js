// React Native Integration Code
// Share this with your teammate

import React, { useState } from 'react';
import { View, Button, Text, Image, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// ⚠️ IMPORTANT: Replace with your actual IP address
const API_URL = 'http://192.168.1.100:5000'; // Change this to your computer's IP

const PlantDiseaseDetection = () => {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Method 1: Using FormData (Recommended)
  const pickImageAndDiagnose = async () => {
    try {
      // Request permission
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permissionResult.granted) {
        alert('Permission to access gallery is required!');
        return;
      }

      // Pick image
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled) {
        const uri = result.assets[0].uri;
        setImage(uri);
        setLoading(true);
        setResult(null);

        // Create FormData
        const formData = new FormData();
        formData.append('image', {
          uri: uri,
          type: 'image/jpeg',
          name: 'plant.jpg',
        });

        // Send to API
        const response = await fetch(`${API_URL}/predict`, {
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const data = await response.json();
        
        if (data.success) {
          setResult(data);
        } else {
          alert('Error: ' + data.error);
        }
        
        setLoading(false);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error: ' + error.message);
      setLoading(false);
    }
  };

  // Method 2: Using Camera
  const takePictureAndDiagnose = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      if (!permissionResult.granted) {
        alert('Permission to access camera is required!');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled) {
        const uri = result.assets[0].uri;
        setImage(uri);
        setLoading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('image', {
          uri: uri,
          type: 'image/jpeg',
          name: 'plant.jpg',
        });

        const response = await fetch(`${API_URL}/predict`, {
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const data = await response.json();
        
        if (data.success) {
          setResult(data);
        } else {
          alert('Error: ' + data.error);
        }
        
        setLoading(false);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error: ' + error.message);
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🌿 Plant Disease Detection</Text>
      
      <View style={styles.buttonContainer}>
        <Button title="📷 Take Photo" onPress={takePictureAndDiagnose} />
        <View style={styles.spacer} />
        <Button title="🖼️ Choose from Gallery" onPress={pickImageAndDiagnose} />
      </View>

      {image && (
        <Image source={{ uri: image }} style={styles.image} />
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0000ff" />
          <Text style={styles.loadingText}>Analyzing plant disease...</Text>
        </View>
      )}

      {result && result.success && (
        <View style={styles.resultContainer}>
          <Text style={styles.sectionTitle}>🎯 Detection Results</Text>
          
          <View style={styles.infoBox}>
            <Text style={styles.label}>Crop:</Text>
            <Text style={styles.value}>{result.prediction.crop}</Text>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.label}>Disease:</Text>
            <Text style={styles.value}>{result.prediction.disease}</Text>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.label}>Confidence:</Text>
            <Text style={styles.value}>{result.prediction.confidence_percentage}</Text>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.label}>Severity:</Text>
            <Text style={styles.value}>{result.prediction.severity}</Text>
          </View>

          {/* Solutions */}
          {result.solution.india && (
            <>
              <Text style={styles.sectionTitle}>💊 Treatment Solutions</Text>
              
              {result.solution.india.organic && (
                <View style={styles.solutionSection}>
                  <Text style={styles.solutionTitle}>🌿 Organic Treatment:</Text>
                  {result.solution.india.organic.map((item, index) => (
                    <Text key={index} style={styles.bulletPoint}>• {item}</Text>
                  ))}
                </View>
              )}

              {result.solution.india.chemical && (
                <View style={styles.solutionSection}>
                  <Text style={styles.solutionTitle}>💊 Chemical Treatment:</Text>
                  {result.solution.india.chemical.map((item, index) => (
                    <Text key={index} style={styles.bulletPoint}>• {item}</Text>
                  ))}
                </View>
              )}

              {result.solution.india.prevention && (
                <View style={styles.solutionSection}>
                  <Text style={styles.solutionTitle}>🛡️ Prevention:</Text>
                  {result.solution.india.prevention.map((item, index) => (
                    <Text key={index} style={styles.bulletPoint}>• {item}</Text>
                  ))}
                </View>
              )}
            </>
          )}

          {/* Healthy plant maintenance */}
          {result.solution.maintenance && (
            <>
              <Text style={styles.sectionTitle}>✅ Maintenance Tips</Text>
              <Text style={styles.message}>{result.solution.message}</Text>
              {result.solution.maintenance.map((item, index) => (
                <Text key={index} style={styles.bulletPoint}>• {item}</Text>
              ))}
            </>
          )}

          {/* Top predictions */}
          <Text style={styles.sectionTitle}>📊 All Predictions</Text>
          {result.all_predictions.map((pred, index) => (
            <View key={index} style={styles.predictionItem}>
              <Text>{pred.label}</Text>
              <Text>{pred.confidence}%</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginVertical: 20,
  },
  buttonContainer: {
    marginVertical: 10,
  },
  spacer: {
    height: 10,
  },
  image: {
    width: '100%',
    height: 300,
    marginVertical: 20,
    borderRadius: 10,
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
  },
  resultContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginVertical: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
  },
  infoBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  value: {
    fontSize: 16,
  },
  solutionSection: {
    marginVertical: 10,
  },
  solutionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  bulletPoint: {
    fontSize: 14,
    marginVertical: 2,
    paddingLeft: 10,
  },
  message: {
    fontSize: 14,
    fontStyle: 'italic',
    marginBottom: 10,
  },
  predictionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 5,
  },
});

export default PlantDiseaseDetection;

// ==============================================================
// INSTALLATION INSTRUCTIONS FOR YOUR TEAMMATE
// ==============================================================

/*
1. Install required packages in React Native project:

   npm install expo-image-picker
   # or
   yarn add expo-image-picker

2. Add to app.json:
   {
     "expo": {
       "plugins": [
         [
           "expo-image-picker",
           {
             "photosPermission": "The app needs access to your photos to detect plant diseases.",
             "cameraPermission": "The app needs access to your camera to take plant photos."
           }
         ]
       ]
     }
   }

3. Update API_URL constant at the top of this file with the server's IP address

4. Import and use the component in your app:
   import PlantDiseaseDetection from './PlantDiseaseDetection';
*/
