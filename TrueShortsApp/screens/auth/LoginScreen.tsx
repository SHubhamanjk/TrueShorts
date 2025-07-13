import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';
import { loginUser } from '../../services/api';

export default function LoginScreen() {
  const navigation = useNavigation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const data = await loginUser(email, password);
      if (data.access_token) {
        await AsyncStorage.setItem('token', data.access_token);
        navigation.reset({ index: 0, routes: [{ name: 'MainApp' }] });
      } else {
        Alert.alert('Login Failed', data.detail || 'Invalid credentials');
      }
    } catch (err) {
      Alert.alert('Login Error', 'Could not login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Image source={require('../../assets/icon.png')} style={styles.logo} />
      <Text style={styles.title}>TrueShorts</Text>
      <TextInput
        style={styles.input}
        placeholder="Phone / Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        <Text style={styles.buttonText}>{loading ? 'Logging in...' : 'Login'}</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.navigate('Signup')}>
        <Text style={styles.link}>Don't have an account? Sign Up</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.navigate('Guest')}>
        <Text style={styles.link}>Skip & Login as Guest</Text>
      </TouchableOpacity>
      <Text style={styles.or}>Sign in with</Text>
      <View style={styles.socialRow}>
        <Image source={require('../../assets/google.webp')} style={styles.socialIcon} />
        <Image source={require('../../assets/apple.jpg')} style={styles.socialIcon} />
        <Image source={require('../../assets/facebook.png')} style={styles.socialIcon} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', padding: 20 },
  logo: { width: 80, height: 80, marginBottom: 16 },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 24, color: '#1a1a1a' },
  input: { width: '100%', height: 48, borderColor: '#ccc', borderWidth: 1, borderRadius: 8, paddingHorizontal: 12, marginBottom: 16, fontSize: 16 },
  button: { width: '100%', height: 48, backgroundColor: '#1976d2', borderRadius: 8, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  link: { color: '#1976d2', marginTop: 8, fontSize: 15 },
  or: { marginVertical: 16, color: '#888', fontSize: 15 },
  socialRow: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center' },
  socialIcon: { width: 36, height: 36, marginHorizontal: 8 },
}); 