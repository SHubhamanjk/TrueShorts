import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';

export default function GuestScreen() {
  const navigation = useNavigation();

  const handleGuest = () => {
    navigation.reset({ index: 0, routes: [{ name: 'MainApp' }] });
  };

  return (
    <View style={styles.container}>
      <Image source={require('../../assets/icon.png')} style={styles.logo} />
      <Text style={styles.title}>Continue as Guest</Text>
      <TouchableOpacity style={styles.button} onPress={handleGuest}>
        <Text style={styles.buttonText}>Enter App</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.navigate('Login')}>
        <Text style={styles.link}>Back to Login</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', padding: 20 },
  logo: { width: 80, height: 80, marginBottom: 16 },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 24, color: '#1a1a1a' },
  button: { width: '100%', height: 48, backgroundColor: '#1976d2', borderRadius: 8, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  link: { color: '#1976d2', marginTop: 8, fontSize: 15 },
}); 