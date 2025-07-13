import React, { useEffect, useState, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, TextInput, Keyboard, Alert, Dimensions, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getNews, saveArticle, searchNews, trackReading, startAIChat, askFollowUp, fetchLatestNews } from '../../services/api';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { useNavigation } from '@react-navigation/native';

const { height } = Dimensions.get('window');

export default function TrendingScreen() {
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [searching, setSearching] = useState(false);
  const [aiSession, setAiSession] = useState<any>(null);
  const [aiInput, setAiInput] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiMessages, setAiMessages] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const readingStart = useRef<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [activeAIArticle, setActiveAIArticle] = useState<string | null>(null);

  const navigation = useNavigation();

  useEffect(() => {
    fetchNews();
  }, []);

  useFocusEffect(
    useCallback(() => {
      let interval: NodeJS.Timeout | null = null;
      const startScheduler = () => {
        interval = setInterval(async () => {
          try {
            const token = await AsyncStorage.getItem('token');
            if (!token) return;
            await fetchLatestNews(token);
            await fetchNews();
          } catch {}
        }, 10 * 60 * 1000); // 10 minutes
      };
      startScheduler();
      return () => {
        if (interval) clearInterval(interval);
      };
    }, [])
  );

  const fetchNews = async () => {
    setLoading(true);
    setError('');
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) throw new Error('Not logged in');
      const data = await getNews(token);
      setNews(Array.isArray(data) ? data : [data]);
    } catch (err: any) {
      setError(err.message || 'Failed to load news');
    } finally {
      setLoading(false);
    }
  };

  const fetchNextArticle = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) throw new Error('Not logged in');
      const data = await getNews(token);
      // Prevent duplicates
      if (news.some(a => a.article_id === data.article_id)) return;
      setNews(prev => [...prev, data]);
    } catch (err: any) {
      setError(err.message || 'Failed to load news');
    }
  };

  const handleSearch = async () => {
    setSearching(true);
    setError('');
    Keyboard.dismiss();
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) throw new Error('Not logged in');
      const data = await searchNews(token, search);
      setNews(Array.isArray(data) ? data : [data]);
      setCurrentIndex(0);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  const handleSave = async (articleId: string) => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) throw new Error('Not logged in');
      const res = await saveArticle(token, articleId);
      Alert.alert('Saved', res.msg || 'Article saved');
    } catch (err: any) {
      Alert.alert('Error', err.message || 'Failed to save article');
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const token = await AsyncStorage.getItem('token');
      if (!token) throw new Error('Not logged in');
      const res = await fetchLatestNews(token);
      if (res.status === 'success') {
        await fetchNews();
      } else {
        Alert.alert('Refresh Error', res.detail || 'Failed to fetch latest news');
      }
    } catch (err: any) {
      Alert.alert('Refresh Error', err.message || 'Failed to fetch latest news');
    } finally {
      setRefreshing(false);
    }
  };

  const handleViewableItemsChanged = useRef(({ viewableItems }: any) => {
    if (viewableItems.length > 0) {
      const newIndex = viewableItems[0].index;
      if (newIndex !== currentIndex) {
        handleTrackReading(currentIndex);
        setCurrentIndex(newIndex);
        readingStart.current = Date.now();
      }
    }
  }).current;

  const handleTrackReading = async (index: number) => {
    if (index < 0 || index >= news.length) return;
    if (readingStart.current) {
      const duration = Math.floor((Date.now() - readingStart.current) / 1000);
      if (duration > 0) {
        try {
          const token = await AsyncStorage.getItem('token');
          if (!token) return;
          console.log('Tracking reading:', { article_id: news[index].article_id, duration });
          const res = await trackReading(token, news[index].article_id, duration);
          console.log('Track reading response:', res);
        } catch (err) {
          console.error('Failed to track reading:', err);
        }
      }
    }
  };

  const handleAIChat = async (articleId: string) => {
    setAiLoading(true);
    setAiSession(null);
    setAiMessages([]);
    try {
      const data = await startAIChat(articleId);
      setAiSession(data.session_id);
      setAiMessages([{ role: 'ai', text: data.analysis || 'AI analysis started.' }]);
    } catch (err: any) {
      Alert.alert('AI Error', err.message || 'Failed to start AI chat');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAIFollowUp = async () => {
    if (!aiSession || !aiInput) return;
    setAiLoading(true);
    try {
      setAiMessages((msgs) => [...msgs, { role: 'user', text: aiInput }]);
      const data = await askFollowUp(aiSession, aiInput);
      setAiMessages((msgs) => [...msgs, { role: 'ai', text: data.answer || JSON.stringify(data) }]);
      setAiInput('');
    } catch (err: any) {
      Alert.alert('AI Error', err.message || 'Failed to get follow-up');
    } finally {
      setAiLoading(false);
    }
  };

  const renderItem = ({ item, index }: any) => (
    <View style={[styles.card, { height: height * 0.8 }]}> 
      <Text style={styles.title}>{item.title}</Text>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 12 }}>
        <Text style={styles.content}>{item.content}</Text>
      </ScrollView>
      <View style={styles.actionsFixed}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => handleSave(item.article_id)}>
          <Ionicons name="bookmark-outline" size={22} color="#1976d2" />
          <Text style={{ color: '#1976d2', marginLeft: 4 }}>Save News</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => {
          navigation.navigate('AIChat', { article: item });
        }}>
          <Ionicons name="chatbubble-ellipses-outline" size={22} color="#1976d2" />
          <Text style={{ color: '#1976d2', marginLeft: 4 }}>Ask AI</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#1976d2" /></View>;
  if (error) return <View style={styles.center}><Text>{error}</Text></View>;

  return (
    <View style={{ flex: 1, backgroundColor: '#fff' }}>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search news..."
          value={search}
          onChangeText={setSearch}
          onSubmitEditing={handleSearch}
        />
        <TouchableOpacity onPress={handleSearch} disabled={searching}>
          <Ionicons name="search" size={24} color="#1976d2" />
        </TouchableOpacity>
        <TouchableOpacity onPress={handleRefresh} disabled={refreshing} style={{ marginLeft: 8 }}>
          <Ionicons name={refreshing ? 'refresh-circle' : 'refresh'} size={28} color={refreshing ? '#888' : '#1976d2'} />
        </TouchableOpacity>
      </View>
      <FlatList
        data={news}
        renderItem={renderItem}
        keyExtractor={(item, index) => item.article_id ? String(item.article_id) : `news-${index}`}
        pagingEnabled
        showsVerticalScrollIndicator={false}
        onViewableItemsChanged={handleViewableItemsChanged}
        viewabilityConfig={{ itemVisiblePercentThreshold: 80 }}
        getItemLayout={(_, index) => ({ length: height * 0.8, offset: height * 0.8 * index, index })}
        onEndReached={fetchNextArticle}
        onEndReachedThreshold={0.5}
        ListEmptyComponent={<Text style={styles.center}>No news found.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  searchRow: { flexDirection: 'row', alignItems: 'center', padding: 10, backgroundColor: '#f5f5f5' },
  searchInput: { flex: 1, height: 40, borderColor: '#ccc', borderWidth: 1, borderRadius: 8, paddingHorizontal: 10, marginRight: 8, backgroundColor: '#fff' },
  card: { backgroundColor: '#fff', borderRadius: 12, margin: 12, padding: 16, elevation: 2, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 4 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#1976d2', marginBottom: 6 },
  meta: { fontSize: 13, color: '#888', marginBottom: 8 },
  content: { fontSize: 16, color: '#222', marginBottom: 12 },
  actions: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  actionBtn: { flexDirection: 'row', alignItems: 'center' },
  aiChatBar: { backgroundColor: '#e3f2fd', borderRadius: 8, padding: 10, marginTop: 10 },
  aiTitle: { fontWeight: 'bold', color: '#1976d2', marginBottom: 4 },
  aiMessages: { maxHeight: 80, marginBottom: 6 },
  aiInputRow: { flexDirection: 'row', alignItems: 'center' },
  aiInput: { flex: 1, height: 36, borderColor: '#ccc', borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, backgroundColor: '#fff', marginRight: 8 },
  actionsFixed: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 8, borderTopWidth: 1, borderColor: '#eee', paddingTop: 8 }
}); 