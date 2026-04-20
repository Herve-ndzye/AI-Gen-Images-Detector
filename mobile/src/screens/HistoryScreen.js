import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getHistory } from '../services/api';

const HistoryScreen = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHistory = async () => {
    try {
      const data = await getHistory();
      setHistory(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchHistory();
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.filename}>{item.filename}</Text>
        <Text style={styles.date}>{item.date}</Text>
      </View>
      <View style={styles.cardBody}>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>AI Prob.</Text>
          <Text style={styles.statValue}>{item.ai_probability}</Text>
        </View>
        <View style={[styles.riskBadge, { backgroundColor: item.risk_level === 'High' ? '#2a0000' : '#001a11' }]}>
          <Text style={[styles.riskText, { color: item.risk_level === 'High' ? '#ff4444' : '#44ff44' }]}>
            {item.risk_level.toUpperCase()} RISK
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Scan History</Text>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#3b82f6" style={{ marginTop: 50 }} />
      ) : (
        <FlatList
          data={history}
          keyExtractor={item => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />}
          ListEmptyComponent={
            <View style={styles.empty}>
              <Ionicons name="documents-outline" size={60} color="#222" />
              <Text style={styles.emptyText}>No scans yet. Try uploading an image!</Text>
            </View>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505' },
  header: { paddingTop: 60, paddingHorizontal: 20, marginBottom: 20 },
  title: { color: '#fff', fontSize: 28, fontWeight: 'bold' },
  list: { paddingHorizontal: 20, paddingBottom: 40 },
  card: { backgroundColor: '#111', borderRadius: 16, padding: 18, marginBottom: 15, borderWidth: 1, borderColor: '#222' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  filename: { color: '#fff', fontSize: 16, fontWeight: 'bold', flex: 1 },
  date: { color: '#555', fontSize: 12 },
  cardBody: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  stat: { gap: 2 },
  statLabel: { color: '#888', fontSize: 11, textTransform: 'uppercase' },
  statValue: { color: '#fff', fontSize: 20, fontWeight: '900' },
  riskBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 10 },
  riskText: { fontSize: 12, fontWeight: 'bold' },
  empty: { marginTop: 100, alignItems: 'center', gap: 15 },
  emptyText: { color: '#444', fontSize: 16, textAlign: 'center' }
});

export default HistoryScreen;
