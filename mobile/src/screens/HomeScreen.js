import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ActivityIndicator, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { analyzeImage } from '../services/api';
import ResultScreen from './ResultScreen';

const HomeScreen = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [imageUri, setImageUri] = useState(null);

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'We need access to your gallery to scan images.');
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      handleAnalysis(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'We need access to your camera to scan images.');
      return;
    }

    let result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      handleAnalysis(result.assets[0].uri);
    }
  };

  const handleAnalysis = async (uri) => {
    setImageUri(uri);
    setLoading(true);
    try {
      const data = await analyzeImage(uri);
      setResult(data);
    } catch (error) {
      Alert.alert('Analysis Failed', 'Could not connect to the verification server.');
      setImageUri(null);
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return <ResultScreen result={result} imageUri={imageUri} onBack={() => setResult(null)} />;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Antigravity</Text>
        <Text style={styles.subtitle}>AI Image Verifier</Text>
      </View>

      <View style={styles.hero}>
        <View style={styles.scannerCircle}>
           <Ionicons name="scan-outline" size={80} color="#3b82f6" />
        </View>
        <Text style={styles.heroText}>Upload any image to check for AI generation signatures.</Text>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.mainButton} onPress={pickImage} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="images-outline" size={24} color="#fff" style={styles.btnIcon} />
              <Text style={styles.buttonText}>Choose from Gallery</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton} onPress={takePhoto} disabled={loading}>
          <Ionicons name="camera-outline" size={24} color="#3b82f6" style={styles.btnIcon} />
          <Text style={styles.secondaryButtonText}>Take a Photo</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Ionicons name="shield-checkmark-outline" size={16} color="#555" />
        <Text style={styles.footerText}>Secured by Forensic AI Analytics</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505', padding: 25, justifyContent: 'space-between' },
  header: { marginTop: 60 },
  title: { color: '#fff', fontSize: 32, fontWeight: '900', letterSpacing: -1 },
  subtitle: { color: '#3b82f6', fontSize: 16, fontWeight: '500', marginTop: 4 },
  hero: { alignItems: 'center', marginVertical: 40 },
  scannerCircle: { width: 200, height: 200, borderRadius: 100, backgroundColor: '#111', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#222' },
  heroText: { color: '#888', textAlign: 'center', marginTop: 30, fontSize: 16, lineHeight: 24, paddingHorizontal: 20 },
  buttonContainer: { gap: 15 },
  mainButton: { backgroundColor: '#3b82f6', height: 65, borderRadius: 20, flexDirection: 'row', justifyContent: 'center', alignItems: 'center' },
  secondaryButton: { backgroundColor: 'transparent', height: 65, borderRadius: 20, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#3b82f6' },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  secondaryButtonText: { color: '#3b82f6', fontSize: 18, fontWeight: 'bold' },
  btnIcon: { marginRight: 12 },
  footer: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginBottom: 20, gap: 8 },
  footerText: { color: '#555', fontSize: 12 },
});

export default HomeScreen;
