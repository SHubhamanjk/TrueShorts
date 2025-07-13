import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity, ScrollView } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getSavedArticle } from '../../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function SavedArticleDetailScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const articleId = route.params?.articleId;
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchArticle = async () => {
      setLoading(true);
      setError('');
      try {
        const token = await AsyncStorage.getItem('token');
        if (!token) throw new Error('Not logged in');
        const data = await getSavedArticle(token, articleId);
        setArticle(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load article');
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [articleId]);

  if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#1976d2" /></View>;
  if (error) return <View style={styles.center}><Text>{error}</Text></View>;
  if (!article) return <View style={styles.center}><Text>Article not found.</Text></View>;

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
        <Ionicons name="arrow-back" size={24} color="#1976d2" />
        <Text style={{ color: '#1976d2', marginLeft: 6 }}>Back</Text>
      </TouchableOpacity>
      <ScrollView>
        <Text style={styles.title}>{article.title}</Text>
        <Text style={styles.meta}>{article.category} | {article.published}</Text>
        <Text style={styles.content}>{article.content}</Text>
        {article.url ? <Text style={styles.url}>Source: {article.url}</Text> : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  backBtn: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#1976d2', marginBottom: 8 },
  meta: { fontSize: 14, color: '#888', marginBottom: 8 },
  content: { fontSize: 16, color: '#222', marginBottom: 12 },
  url: { fontSize: 14, color: '#1976d2', marginTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
}); 