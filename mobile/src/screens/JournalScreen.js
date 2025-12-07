import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const JournalScreen = () => {
    return (
        <SafeAreaView style={styles.container}>
            <Text style={styles.header}>Journal</Text>
            <View style={styles.content}>
                <Text style={styles.text}>Journal feature coming soon...</Text>
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f172a',
    },
    header: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#f8fafc',
        padding: 16,
    },
    content: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    text: {
        color: '#94a3b8',
        fontSize: 16,
    },
});

export default JournalScreen;
