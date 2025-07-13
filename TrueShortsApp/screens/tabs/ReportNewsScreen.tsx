import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Keyboard, Alert } from 'react-native';

export default function ReportNewsScreen() {
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    Keyboard.dismiss();
    try {
      // Placeholder: Replace with actual API call if endpoint is available
      await new Promise((resolve) => setTimeout(resolve, 1000));
      Alert.alert('Report Submitted', 'Thank you for your feedback!');
      setReport('');
    } catch (err: any) {
      Alert.alert('Error', 'Failed to submit report.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Report News or Issue</Text>
      <TextInput
        style={styles.input}
        placeholder="Describe the issue or report a news article..."
        value={report}
        onChangeText={setReport}
        multiline
        numberOfLines={4}
      />
      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={loading || !report}>
        <Text style={styles.buttonText}>{loading ? 'Submitting...' : 'Submit Report'}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 20, justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', color: '#1976d2', marginBottom: 16 },
  input: { width: '100%', minHeight: 80, borderColor: '#ccc', borderWidth: 1, borderRadius: 8, paddingHorizontal: 12, marginBottom: 16, fontSize: 16, textAlignVertical: 'top' },
  button: { width: '100%', height: 48, backgroundColor: '#1976d2', borderRadius: 8, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
}); 