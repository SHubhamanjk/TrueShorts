import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from './screens/auth/LoginScreen';
import SignupScreen from './screens/auth/SignupScreen';
import GuestScreen from './screens/auth/GuestScreen';
import MainApp from './screens/MainApp';
import AIChatScreen from './screens/tabs/AIChatScreen';
import SavedArticleDetailScreen from './screens/tabs/SavedArticleDetailScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  console.log("App.tsx loaded");
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Signup" component={SignupScreen} />
        <Stack.Screen name="Guest" component={GuestScreen} />
        <Stack.Screen name="MainApp" component={MainApp} />
        <Stack.Screen name="AIChat" component={AIChatScreen} options={{ presentation: 'modal', headerShown: false }} />
        <Stack.Screen name="SavedArticleDetail" component={SavedArticleDetailScreen} options={{ title: 'Saved Article' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
