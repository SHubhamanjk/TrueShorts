import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { startAIChat, askFollowUp } from '../../services/api';

export default function AIChatScreen() {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const article = route.params?.article;
  const [aiSession, setAiSession] = useState<string | null>(null);
  const [aiMessages, setAiMessages] = useState<any[]>([]);
  const [aiInput, setAiInput] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (article?.article_id) {
      handleAIChat(article.article_id);
    }
  }, [article]);

  const handleAIChat = async (articleId: string) => {
    setAiLoading(true);
    setAiSession(null);
    setAiMessages([]);
    setError('');
    try {
      // Only use LLM for analysis; backend tools (DuckDuckGo, Wikipedia) are commented out or disabled.
      const data = await startAIChat(articleId);
      if (!data || !data.analysis) {
        throw new Error('AI analysis not available.');
      }
      setAiSession(data.session_id);
      setAiMessages([{ role: 'ai', text: data.analysis }]);
    } catch (err: any) {
      setError(err.message || 'Failed to start AI chat');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAIFollowUp = async () => {
    if (!aiSession) {
      setError('AI session not initialized. Try reloading the analysis.');
      return;
    }
    if (!aiInput) return;
    setAiLoading(true);
    setError('');
    try {
      console.log('Sending follow-up:', { sessionId: aiSession, question: aiInput });
      setAiMessages((msgs) => [...msgs, { role: 'user', text: aiInput }]);
      const data = await askFollowUp(aiSession, aiInput);
      console.log('Follow-up response:', data);
      setAiMessages((msgs) => [...msgs, { role: 'ai', text: data.answer || JSON.stringify(data) }]);
      setAiInput('');
    } catch (err: any) {
      setError(err.message || 'Failed to get follow-up');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
        <Ionicons name="arrow-back" size={24} color="#1976d2" />
        <Text style={{ color: '#1976d2', marginLeft: 6 }}>Back to News</Text>
      </TouchableOpacity>
      <Text style={styles.title}>{article?.title}</Text>
      <Text style={styles.content}>{article?.content}</Text>
      <Text style={styles.aiTitle}>AI Analysis & Chat</Text>
      <View style={styles.aiInputRow}>
        <TextInput
          style={styles.aiInput}
          placeholder="Ask a follow-up..."
          value={aiInput}
          onChangeText={setAiInput}
          editable={!aiLoading}
        />
        <TouchableOpacity onPress={handleAIFollowUp} disabled={aiLoading || !aiInput}>
          <Ionicons name="send" size={22} color={aiLoading || !aiInput ? '#888' : '#1976d2'} />
        </TouchableOpacity>
      </View>
      <ScrollView style={styles.aiMessages} contentContainerStyle={{ paddingBottom: 10 }}>
        {aiLoading && <ActivityIndicator size="small" color="#1976d2" style={{ marginTop: 8 }} />}
        {error ? <Text style={styles.error}>{error}</Text> : null}
        {!aiLoading && !error && aiMessages.map((msg, i) => (
          <Text key={i} style={{ color: msg.role === 'ai' ? '#1976d2' : '#333', marginBottom: 6 }}>
            <Text style={{ fontWeight: 'bold' }}>{msg.role === 'ai' ? 'AI: ' : 'You: '}</Text>{msg.text}
          </Text>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  backBtn: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#1976d2', marginBottom: 6 },
  content: { fontSize: 16, color: '#222', marginBottom: 12 },
  aiTitle: { fontWeight: 'bold', color: '#1976d2', marginBottom: 8, fontSize: 16 },
  aiMessages: { flex: 1, marginBottom: 8 },
  aiInputRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8 },
  aiInput: { flex: 1, height: 36, borderColor: '#ccc', borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, backgroundColor: '#fff', marginRight: 8 },
  error: { color: 'red', marginBottom: 8 },
}); 