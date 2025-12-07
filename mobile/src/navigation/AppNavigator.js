import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { Home, Activity, BookOpen } from 'lucide-react-native';
import { theme } from '../theme';

import DashboardScreen from '../screens/DashboardScreen';
import SignalsScreen from '../screens/SignalsScreen';
import JournalScreen from '../screens/JournalScreen';

const Tab = createBottomTabNavigator();

const AppNavigator = () => {
    return (
        <NavigationContainer>
            <Tab.Navigator
                screenOptions={{
                    headerShown: false,
                    tabBarStyle: {
                        backgroundColor: theme.colors.bgMain,
                        borderTopColor: theme.colors.borderElevated,
                    },
                    tabBarActiveTintColor: theme.colors.accentPrimary,
                    tabBarInactiveTintColor: theme.colors.textMuted,
                }}
            >
                <Tab.Screen
                    name="Dashboard"
                    component={DashboardScreen}
                    options={{
                        tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
                    }}
                />
                <Tab.Screen
                    name="Signals"
                    component={SignalsScreen}
                    options={{
                        tabBarIcon: ({ color, size }) => <Activity color={color} size={size} />,
                    }}
                />
                <Tab.Screen
                    name="Journal"
                    component={JournalScreen}
                    options={{
                        tabBarIcon: ({ color, size }) => <BookOpen color={color} size={size} />,
                    }}
                />
            </Tab.Navigator>
        </NavigationContainer>
    );
};

export default AppNavigator;
