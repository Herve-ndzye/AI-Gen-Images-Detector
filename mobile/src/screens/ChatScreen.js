import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { BlurView } from 'expo-blur';
import { Ionicons } from '@expo/vector-icons';
import { chatWithAI } from '../services/api';

const ChatScreen = ({ analysis, onBack }) => {
  const [messages, setMessages] = useState([
    { id: '1', role: 'ai', content: "Hello! I'm your Forensic AI Assistant. Based on my analysis, I've detected some suspicious patterns in this image. What would you like me to explain?" }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const data = await chatWithAI(currentInput, analysis);
      const aiMsg = { id: (Date.now() + 1).toString(), role: 'ai', content: data.response };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg = { id: 'err', role: 'ai', content: "Sorry, I'm having trouble connecting to my knowledge base right now." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }) => (
    <View style={[styles.messageBubble, item.role === 'ai' ? styles.aiBubble : styles.userBubble]}>
      <Text style={styles.messageText}>{item.content}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <BlurView intensity={80} tint="dark" style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.closeBtn}>
          <Ionicons name="close" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>AI Forensic Expert</Text>
        <View style={{ width: 40 }} />
      </BlurView>

      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        inverted={false}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={20}
      >
        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            placeholder="Ask about ELA, noise, or grids..."
            placeholderTextColor="#666"
            value={input}
            onChangeText={setInput}
            multiline
          />
          <TouchableOpacity style={styles.sendBtn} onPress={handleSend}>
            {loading ? <ActivityIndicator size="small" color="#fff" /> : <Ionicons name="send" size={20} color="#fff" />}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  header: { height: 100, paddingTop: 40, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, borderBottomWidth: 1, borderColor: '#222' },
  headerTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  closeBtn: { padding: 8 },
  listContent: { padding: 20, paddingBottom: 40 },
  messageBubble: { padding: 15, borderRadius: 20, marginBottom: 15, maxWidth: '85%' },
  aiBubble: { backgroundColor: '#1a1a1a', alignSelf: 'flex-start', borderBottomLeftRadius: 4 },
  userBubble: { backgroundColor: '#3b82f6', alignSelf: 'flex-end', borderBottomRightRadius: 4 },
  messageText: { color: '#fff', fontSize: 15, lineHeight: 22 },
  inputArea: { flexDirection: 'row', padding: 15, backgroundColor: '#111', borderTopWidth: 1, borderColor: '#222', alignItems: 'flex-end', paddingBottom: 30 },
  textInput: { flex: 1, backgroundColor: '#000', borderRadius: 20, paddingHorizontal: 20, paddingVertical: 10, color: '#fff', maxHeight: 100, fontSize: 16 },
  sendBtn: { width: 45, height: 45, borderRadius: 23, backgroundColor: '#3b82f6', justifyContent: 'center', alignItems: 'center', marginLeft: 10 }
});

export default ChatScreen;
