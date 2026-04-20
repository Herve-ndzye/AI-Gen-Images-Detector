import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity } from 'react-native';
import { BlurView } from 'expo-blur';
import { Ionicons } from '@expo/vector-icons';

import ChatScreen from './ChatScreen';

const ResultScreen = ({ result, imageUri, onBack }) => {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const isHighRisk = result.summary.risk_level === 'High';
  const regions = result.analysis.suspicious_regions || [];

  if (showChat) {
    return <ChatScreen analysis={result} onBack={() => setShowChat(false)} />;
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header Image with Overlays */}
      <View style={styles.imageContainer}>
        <Image source={{ uri: imageUri }} style={styles.image} />
        
        {/* Render Suspicious Boxes */}
        {regions.map((region, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.regionBox,
              {
                left: `${(region.x / 10.24)}%`, // Scaling based on 1024px backend width
                top: `${(region.y / 10.24)}%`,
                width: `${(region.width / 10.24)}%`,
                height: `${(region.height / 10.24)}%`,
              }
            ]}
            onPress={() => setSelectedRegion(region)}
          />
        ))}

        {selectedRegion && (
          <BlurView intensity={90} tint="dark" style={styles.tooltip}>
            <View style={styles.tooltipHeader}>
              <Ionicons name="warning" size={16} color="#ff4444" />
              <Text style={styles.tooltipTitle}>Region Flagged</Text>
              <TouchableOpacity onPress={() => setSelectedRegion(null)}>
                <Ionicons name="close-circle" size={20} color="#fff" />
              </TouchableOpacity>
            </View>
            <Text style={styles.tooltipText}>{selectedRegion.reason}</Text>
          </BlurView>
        )}

        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <BlurView intensity={80} tint="dark" style={styles.backBlur}>
            <Ionicons name="chevron-back" size={24} color="#fff" />
          </BlurView>
        </TouchableOpacity>
      </View>

      {/* Main Score Card */}
      <View style={styles.content}>
        {/* Regions Count Badge */}
        {regions.length > 0 && (
          <View style={styles.anomalyBadge}>
            <Ionicons name="alert-circle" size={14} color="#ffb000" />
            <Text style={styles.anomalyText}>{regions.length} Anomalies Detected</Text>
          </View>
        )}
        <View style={[styles.scoreCard, isHighRisk ? styles.riskBg : styles.safeBg]}>
          <Text style={styles.label}>AI PROBABILITY</Text>
          <Text style={styles.score}>{result.summary.ai_probability}</Text>
          <Text style={styles.verdict}>{result.summary.verdict}</Text>
        </View>

        {/* Stats Grid */}
        <View style={styles.grid}>
          <View style={styles.gridItem}>
            <Text style={styles.gridLabel}>Authenticity</Text>
            <Text style={styles.gridValue}>{result.summary.authenticity_trust}</Text>
          </View>
          <View style={styles.gridItem}>
            <Text style={styles.gridLabel}>Risk Level</Text>
            <Text style={[styles.gridValue, { color: isHighRisk ? '#ff4444' : '#44ff44' }]}>
              {result.summary.risk_level}
            </Text>
          </View>
        </View>

        {/* Explanations */}
        <Text style={styles.sectionTitle}>Detailed Analysis</Text>
        {result.analysis.explanations.map((item, index) => (
          <View key={index} style={styles.explanationBox}>
            <Ionicons name="analytics-outline" size={18} color="#aaa" />
            <Text style={styles.explanationText}>{item}</Text>
          </View>
        ))}

        {/* Metadata section */}
        <View style={styles.metadataBox}>
          <Text style={styles.metaTitle}>Digital Fingerprint</Text>
          <Text style={styles.metaText}>Camera: {result.metadata_summary.camera}</Text>
          <Text style={styles.metaText}>Created: {result.metadata_summary.timestamp}</Text>
        </View>

        {/* Chat Button */}
        <TouchableOpacity style={styles.chatButton} onPress={() => setShowChat(true)}>
            <Text style={styles.chatButtonText}>Ask AI Assistant</Text>
            <Ionicons name="chatbubble-ellipses-outline" size={20} color="#fff" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  imageContainer: { width: '100%', height: 350, position: 'relative' },
  image: { width: '100%', height: '100%', resizeMode: 'cover' },
  regionBox: {
    position: 'absolute',
    borderWidth: 2,
    borderColor: '#ff4444',
    backgroundColor: 'rgba(255, 68, 68, 0.1)',
    borderRadius: 4,
  },
  tooltip: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    padding: 15,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    overflow: 'hidden',
  },
  tooltipHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 5, gap: 8 },
  tooltipTitle: { color: '#ff4444', fontWeight: 'bold', fontSize: 13, flex: 1 },
  tooltipText: { color: '#fff', fontSize: 14, lineHeight: 20 },
  anomalyBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 176, 0, 0.1)',
    alignSelf: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 176, 0, 0.2)',
    marginBottom: 15,
    gap: 6
  },
  anomalyText: { color: '#ffb000', fontSize: 12, fontWeight: '600' },
  backButton: { position: 'absolute', top: 50, left: 20 },
  backBlur: { borderRadius: 20, padding: 8, overflow: 'hidden' },
  content: { padding: 20, marginTop: -30, backgroundColor: '#0a0a0a', borderTopLeftRadius: 30, borderTopRightRadius: 30 },
  scoreCard: { padding: 30, borderRadius: 24, alignItems: 'center', marginBottom: 20 },
  riskBg: { backgroundColor: '#2a0000', borderActive: 1, borderContent: '#ff4444' },
  safeBg: { backgroundColor: '#001a11', borderActive: 1, borderContent: '#44ff44' },
  label: { color: '#aaa', fontSize: 12, fontWeight: 'bold', letterSpacing: 1 },
  score: { color: '#fff', fontSize: 48, fontWeight: '900', marginVertical: 5 },
  verdict: { color: '#fff', fontSize: 18, opacity: 0.8 },
  grid: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 30 },
  gridItem: { backgroundColor: '#1a1a1a', padding: 15, borderRadius: 16, width: '48%' },
  gridLabel: { color: '#888', fontSize: 12 },
  gridValue: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginTop: 5 },
  sectionTitle: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginBottom: 15 },
  explanationBox: { flexDirection: 'row', backgroundColor: '#1a1a1a', padding: 15, borderRadius: 12, marginBottom: 10, alignItems: 'center' },
  explanationText: { color: '#ccc', marginLeft: 10, flex: 1, fontSize: 14 },
  metadataBox: { backgroundColor: '#111', padding: 20, borderRadius: 16, marginTop: 10 },
  metaTitle: { color: '#888', fontSize: 12, textTransform: 'uppercase', marginBottom: 8 },
  metaText: { color: '#fff', fontSize: 14, marginBottom: 4 },
  chatButton: { backgroundColor: '#3b82f6', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', padding: 18, borderRadius: 16, marginTop: 25 },
  chatButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 16, marginRight: 10 },
});

export default ResultScreen;
