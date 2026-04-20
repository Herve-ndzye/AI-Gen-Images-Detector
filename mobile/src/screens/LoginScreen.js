import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

import api from '../services/api';

const LoginScreen = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    
    setLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });
      onLogin(response.data.user);
    } catch (error) {
      Alert.alert('Login Failed', error.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.topSection}>
        <View style={styles.logoBadge}>
          <Ionicons name="finger-print" size={40} color="#3b82f6" />
        </View>
        <Text style={styles.welcome}>Welcome back</Text>
        <Text style={styles.subWelcome}>Sign in to verify your images</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Email Address</Text>
          <View style={styles.inputWrapper}>
             <Ionicons name="mail-outline" size={20} color="#555" style={styles.inputIcon} />
             <TextInput 
                style={styles.input}
                placeholder="name@example.com"
                placeholderTextColor="#444"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
             />
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Password</Text>
          <View style={styles.inputWrapper}>
             <Ionicons name="lock-closed-outline" size={20} color="#555" style={styles.inputIcon} />
             <TextInput 
                style={styles.input}
                placeholder="••••••••"
                placeholderTextColor="#444"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
             />
          </View>
        </View>

        <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
           <Text style={styles.loginText}>Sign In</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.registerLink}>
           <Text style={styles.registerText}>Don't have an account? <Text style={styles.blueText}>Sign Up</Text></Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505', padding: 25 },
  topSection: { marginTop: 100, alignItems: 'center' },
  logoBadge: { width: 80, height: 80, borderRadius: 20, backgroundColor: '#111', justifyContent: 'center', alignItems: 'center', marginBottom: 25, borderWidth: 1, borderColor: '#222' },
  welcome: { color: '#fff', fontSize: 28, fontWeight: 'bold' },
  subWelcome: { color: '#888', fontSize: 16, marginTop: 8 },
  form: { marginTop: 50 },
  inputGroup: { marginBottom: 20 },
  label: { color: '#888', fontSize: 14, marginBottom: 10, fontWeight: '500' },
  inputWrapper: { height: 60, backgroundColor: '#111', borderRadius: 16, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 15, borderWidth: 1, borderColor: '#222' },
  inputIcon: { marginRight: 12 },
  input: { flex: 1, color: '#fff', fontSize: 16 },
  loginButton: { backgroundColor: '#3b82f6', height: 60, borderRadius: 16, justifyContent: 'center', alignItems: 'center', marginTop: 30 },
  loginText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  registerLink: { marginTop: 25, alignItems: 'center' },
  registerText: { color: '#888', fontSize: 14 },
  blueText: { color: '#3b82f6', fontWeight: 'bold' }
});

export default LoginScreen;
