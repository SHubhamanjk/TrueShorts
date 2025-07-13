import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import TrendingScreen from './tabs/TrendingScreen';
import ValidateNewsScreen from './tabs/ValidateNewsScreen';
import ReportNewsScreen from './tabs/ReportNewsScreen';
import ProfileScreen from './tabs/ProfileScreen';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();

export default function MainApp() {
  return (
    <Tab.Navigator
      initialRouteName="Trending"
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ color, size }) => {
          let iconName = 'home';
          if (route.name === 'Trending') iconName = 'flame';
          else if (route.name === 'Validate') iconName = 'checkmark-circle';
          else if (route.name === 'Report') iconName = 'alert-circle';
          else if (route.name === 'Profile') iconName = 'person';
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1976d2',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Trending" component={TrendingScreen} />
      <Tab.Screen name="Validate" component={ValidateNewsScreen} />
      <Tab.Screen name="Report" component={ReportNewsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
} 