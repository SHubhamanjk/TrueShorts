import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Keyboard } from 'react-native';
import { verifyClaim } from '../../services/api';

export default function ValidateNewsScreen() {
  const [claim, setClaim] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleVerify = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    Keyboard.dismiss();
    try {
      const data = await verifyClaim(claim);
      setResult(data);
    } catch (err: any) {
      setError('Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Fake News Verification</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter a claim to verify..."
        value={claim}
        onChangeText={setClaim}
      />
      <TouchableOpacity style={styles.button} onPress={handleVerify} disabled={loading || !claim}>
        <Text style={styles.buttonText}>{loading ? 'Verifying...' : 'Verify'}</Text>
      </TouchableOpacity>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {result && (
        <View style={styles.resultBox}>
          <Text style={styles.resultTitle}>Result:</Text>
          {result.verdict && (
            <Text style={{ fontWeight: 'bold', marginBottom: 4 }}>
              Verdict: <Text style={{ color: result.verdict === 'FAKE' ? 'red' : 'green' }}>{result.verdict}</Text>
            </Text>
          )}
          {result.explanation && (
            <Text style={styles.resultText}>Explanation: {result.explanation}</Text>
          )}
          {!result.verdict && !result.explanation && (
            <Text style={styles.resultText}>{JSON.stringify(result)}</Text>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 20, justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', color: '#1976d2', marginBottom: 16 },
  input: { width: '100%', height: 48, borderColor: '#ccc', borderWidth: 1, borderRadius: 8, paddingHorizontal: 12, marginBottom: 16, fontSize: 16 },
  button: { width: '100%', height: 48, backgroundColor: '#1976d2', borderRadius: 8, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  error: { color: '#e53935', marginBottom: 8 },
  resultBox: { backgroundColor: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 16 },
  resultTitle: { fontWeight: 'bold', color: '#1976d2', marginBottom: 4 },
  resultText: { fontSize: 15, color: '#333' },
}); 