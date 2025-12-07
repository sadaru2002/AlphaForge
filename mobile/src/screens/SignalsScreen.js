import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import client from '../api/client';
import { theme } from '../theme';
import * as Clipboard from 'expo-clipboard';

const SignalItem = ({ signal }) => {
    const isBuy = signal.direction === 'BUY';

    const handleCopy = async () => {
        const text = `${signal.direction} ${signal.symbol}
Entry: ${signal.entry.toFixed(5)}
Stop Loss: ${signal.stop_loss.toFixed(5)}
TP1: ${signal.tp1.toFixed(5)}
${signal.tp2 ? `TP2: ${signal.tp2.toFixed(5)}` : ''}
Confidence: ${signal.confidence_score}%`;

        await Clipboard.setStringAsync(text);
    };

    return (
        <View style={[styles.signalCard, { borderLeftColor: isBuy ? theme.colors.accentPrimary : theme.colors.accentDanger }]}>
            <View style={styles.signalHeader}>
                <View style={styles.headerLeft}>
                    <Text style={styles.directionEmoji}>{isBuy ? '🟢' : '🔴'}</Text>
                    <Text style={[styles.direction, { color: isBuy ? theme.colors.accentPrimary : theme.colors.accentDanger }]}>
                        {signal.direction}
                    </Text>
                </View>
                <View style={styles.badges}>
                    <View style={[styles.badge, { backgroundColor: theme.colors.accentInfo }]}>
                        <Text style={styles.badgeText}>{signal.symbol}</Text>
                    </View>
                    <View style={[styles.badge, { backgroundColor: theme.colors.accentSuccess }]}>
                        <Text style={styles.badgeText}>{signal.confidence_score || 0}%</Text>
                    </View>
                </View>
            </View>

            <View style={styles.priceSection}>
                <View style={styles.priceItem}>
                    <Text style={styles.priceLabel}>Entry</Text>
                    <Text style={styles.priceValue}>{signal.entry.toFixed(5)}</Text>
                </View>
                <View style={[styles.priceItem, styles.borderLeft]}>
                    <Text style={[styles.priceLabel, { color: theme.colors.accentDanger }]}>SL</Text>
                    <Text style={styles.priceValue}>{signal.stop_loss.toFixed(5)}</Text>
                </View>
                <View style={[styles.priceItem, styles.borderLeft]}>
                    <Text style={[styles.priceLabel, { color: theme.colors.accentPrimary }]}>TP1</Text>
                    <Text style={styles.priceValue}>{signal.tp1.toFixed(5)}</Text>
                </View>
            </View>

            {signal.reasoning && (
                <View style={styles.reasoningSection}>
                    <Text style={styles.reasoningTitle}>🤖 AI Analysis:</Text>
                    <Text style={styles.reasoningText} numberOfLines={3}>
                        {signal.reasoning}
                    </Text>
                </View>
            )}

            <TouchableOpacity style={styles.copyButton} onPress={handleCopy}>
                <Text style={styles.copyButtonText}>Copy Signal Details</Text>
            </TouchableOpacity>
        </View>
    );
};

const SignalsScreen = () => {
    const [signals, setSignals] = useState([]);
    const [refreshing, setRefreshing] = useState(false);

    const fetchSignals = async () => {
        try {
            const response = await client.get('/api/signals');
            setSignals(response.data.signals || []);
        } catch (error) {
            console.error('Error fetching signals:', error);
        }
    };

    const onRefresh = React.useCallback(() => {
        setRefreshing(true);
        fetchSignals().then(() => setRefreshing(false));
    }, []);

    useEffect(() => {
        fetchSignals();
    }, []);

    return (
        <SafeAreaView style={styles.container}>
            <Text style={styles.header}>Signals</Text>
            <FlatList
                data={signals}
                renderItem={({ item }) => <SignalItem signal={item} />}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.listContent}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
                ListEmptyComponent={
                    <Text style={styles.emptyText}>No signals available</Text>
                }
            />
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: theme.colors.bgMain,
    },
    header: {
        fontSize: theme.typography.h2.fontSize,
        fontWeight: 'bold',
        color: theme.colors.textPrimary,
        padding: theme.spacing.md,
    },
    listContent: {
        padding: theme.spacing.md,
    },
    signalCard: {
        backgroundColor: theme.colors.bgCard,
        borderRadius: theme.borderRadius.card,
        padding: theme.spacing.md,
        marginBottom: theme.spacing.md,
        borderWidth: 1,
        borderColor: theme.colors.borderSubtle,
        borderLeftWidth: 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 4,
        elevation: 5,
    },
    signalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: theme.spacing.md,
    },
    headerLeft: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    directionEmoji: {
        fontSize: 20,
        marginRight: theme.spacing.sm,
    },
    direction: {
        fontSize: theme.typography.h3.fontSize,
        fontWeight: 'bold',
    },
    badges: {
        flexDirection: 'row',
        gap: theme.spacing.xs,
    },
    badge: {
        paddingHorizontal: theme.spacing.sm,
        paddingVertical: 4,
        borderRadius: theme.borderRadius.badge,
    },
    badgeText: {
        color: theme.colors.bgMain,
        fontWeight: 'bold',
        fontSize: theme.typography.tiny.fontSize,
    },
    priceSection: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        backgroundColor: theme.colors.bgElevated,
        borderRadius: theme.borderRadius.input,
        padding: theme.spacing.md,
        marginBottom: theme.spacing.md,
    },
    priceItem: {
        flex: 1,
        alignItems: 'center',
    },
    borderLeft: {
        borderLeftWidth: 1,
        borderLeftColor: theme.colors.borderSubtle,
    },
    priceLabel: {
        fontSize: theme.typography.small.fontSize,
        color: theme.colors.textSecondary,
        marginBottom: 4,
    },
    priceValue: {
        fontSize: theme.typography.body.fontSize,
        color: theme.colors.textPrimary,
        fontWeight: 'bold',
    },
    reasoningSection: {
        borderTopWidth: 1,
        borderTopColor: theme.colors.borderSubtle,
        paddingTop: theme.spacing.md,
        marginBottom: theme.spacing.md,
    },
    reasoningTitle: {
        fontSize: theme.typography.small.fontSize,
        color: theme.colors.accentPrimary,
        fontWeight: '600',
        marginBottom: theme.spacing.xs,
    },
    reasoningText: {
        fontSize: theme.typography.small.fontSize,
        color: theme.colors.textSecondary,
        lineHeight: 18,
    },
    copyButton: {
        backgroundColor: theme.colors.accentPrimary,
        paddingVertical: theme.spacing.sm,
        borderRadius: theme.borderRadius.button,
        alignItems: 'center',
    },
    copyButtonText: {
        color: theme.colors.bgMain,
        fontWeight: 'bold',
        fontSize: theme.typography.body.fontSize,
    },
    emptyText: {
        color: theme.colors.textMuted,
        textAlign: 'center',
        marginTop: theme.spacing.xl,
        fontSize: theme.typography.body.fontSize,
    },
});

export default SignalsScreen;
