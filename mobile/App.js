import React, { useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import HistoryScreen from './src/screens/HistoryScreen';

const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#0a0a0a',
          borderTopWidth: 1,
          borderTopColor: '#222',
          height: 90,
          paddingBottom: 30,
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#555',
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Home') iconName = focused ? 'scan' : 'scan-outline';
          else if (route.name === 'History') iconName = focused ? 'time' : 'time-outline';
          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="History" component={HistoryScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  const [user, setUser] = useState(null);

  return (
    <NavigationContainer>
      <StatusBar style="light" />
      {!user ? (
        <LoginScreen onLogin={setUser} />
      ) : (
        <MainTabs />
      )}
    </NavigationContainer>
  );
}
