import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ errorInfo });
    }

    render() {
        if (this.state.hasError) {
            return (
                <View style={styles.container}>
                    <ScrollView style={styles.scroll}>
                        <Text style={styles.title}>Something went wrong.</Text>
                        <Text style={styles.error}>{this.state.error && this.state.error.toString()}</Text>
                        <Text style={styles.stack}>
                            {this.state.errorInfo && this.state.errorInfo.componentStack}
                        </Text>
                    </ScrollView>
                </View>
            );
        }

        return this.props.children;
    }
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        padding: 20,
        justifyContent: 'center',
    },
    scroll: {
        flex: 1,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 10,
        color: 'red',
    },
    error: {
        fontSize: 16,
        color: 'black',
        marginBottom: 10,
    },
    stack: {
        fontSize: 12,
        color: 'gray',
        fontFamily: 'monospace',
    },
});

export default ErrorBoundary;
