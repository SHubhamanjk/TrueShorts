import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Button, FlatList, TouchableOpacity, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';
import { getProfile, getSavedArticles } from '../../services/api';

export default function ProfileScreen() {
  const navigation = useNavigation();
  const [profile, setProfile] = useState<any>(null);
  const [saved, setSaved] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');
      try {
        const token = await AsyncStorage.getItem('token');
        if (!token) throw new Error('Not logged in');
        const profileData = await getProfile(token);
        const savedData = await getSavedArticles(token);
        setProfile(profileData);
        setSaved(savedData);
      } catch (err: any) {
        setError(err.message || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLogout = async () => {
    await AsyncStorage.removeItem('token');
    navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
  };

  if (loading) return <View style={styles.container}><Text>Loading...</Text></View>;
  if (error) return <View style={styles.container}><Text>{error}</Text></View>;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>
      <Text style={styles.label}>User ID: {profile?.user_id || 'Unknown'}</Text>
      <Text style={styles.label}>Name: {profile?.name || 'Unknown'}</Text>
      <Text style={styles.label}>Gender: {profile?.gender || 'Unknown'}</Text>
      <Text style={styles.label}>Email: {profile?.email || 'Unknown'}</Text>
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>
      <Text style={styles.title}>Saved Articles</Text>
      <FlatList
        data={profile?.saved_articles || []}
        keyExtractor={item => item.article_id || item.title}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => {
            if (item.article_id) {
              navigation.navigate('SavedArticleDetail', { articleId: item.article_id });
            } else {
              Alert.alert('Error', 'This saved article is missing an ID and cannot be opened.');
            }
          }}>
            <View style={styles.articleCard}>
              <Text style={styles.articleTitle}>{item.title}</Text>
              <Text numberOfLines={2} style={styles.articleContent}>{item.content}</Text>
            </View>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text>No saved articles.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 20 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#1976d2', marginVertical: 12 },
  label: { fontSize: 16, marginBottom: 4 },
  logoutButton: { backgroundColor: '#e53935', padding: 10, borderRadius: 8, marginVertical: 10, alignItems: 'center' },
  logoutText: { color: '#fff', fontWeight: 'bold' },
  articleCard: { backgroundColor: '#f5f5f5', padding: 12, borderRadius: 8, marginVertical: 6 },
  articleTitle: { fontWeight: 'bold', fontSize: 16, color: '#1976d2' },
  articleContent: { fontSize: 14, color: '#333' },
}); 