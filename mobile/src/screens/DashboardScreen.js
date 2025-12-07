import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LineChart } from 'react-native-chart-kit';
import { Target, Activity, DollarSign, TrendingUp } from 'lucide-react-native';
import client from '../api/client';
import StatsCard from '../components/StatsCard';
import LiveTicker from '../components/LiveTicker';
import { theme } from '../theme';

const DashboardScreen = () => {
    const [stats, setStats] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(null);

    const fetchStats = async () => {
        try {
            setError(null);
            const response = await client.get('/api/stats');
            setStats(response.data);
        } catch (error) {
            console.error('Error fetching stats:', error);
            setError(error.message || 'Something went wrong');
        }
    };

    const onRefresh = React.useCallback(() => {
        setRefreshing(true);
        fetchStats().then(() => setRefreshing(false));
    }, []);

    useEffect(() => {
        fetchStats();
    }, []);

    const chartConfig = {
        backgroundGradientFrom: theme.colors.bgCard,
        backgroundGradientTo: theme.colors.bgCard,
        color: (opacity = 1) => `rgba(127, 255, 0, ${opacity})`,
        strokeWidth: 2,
        barPercentage: 0.5,
        useShadowColorFromDataset: false,
        decimalPlaces: 0,
        labelColor: (opacity = 1) => `rgba(160, 174, 192, ${opacity})`,
    };

    const data = {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        datasets: [
            {
                data: [20, 45, 28, 80, 99, 43],
                color: (opacity = 1) => `rgba(127, 255, 0, ${opacity})`,
                strokeWidth: 2
            }
        ],
        legend: ["Profit Trend"]
    };

    return (
        <SafeAreaView style={styles.container}>
            <LiveTicker />

            <ScrollView
                contentContainerStyle={styles.scrollContent}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
            >
                <Text style={styles.header}>AlphaForge Dashboard</Text>

                {error && (
                    <View style={styles.errorContainer}>
                        <Text style={styles.errorText}>Error: {error}</Text>
                    </View>
                )}

                <View style={styles.statsGrid}>
                    <StatsCard
                        title="Win Rate"
                        value={stats ? `${(stats.win_rate * 100).toFixed(1)}%` : '--'}
                        subValue="Target: 70%+"
                        type={stats?.win_rate >= 0.7 ? 'success' : 'warning'}
                        icon={Target}
                    />
                    <StatsCard
                        title="Net Profit"
                        value={stats ? `$${stats.profit_loss.toFixed(2)}` : '--'}
                        subValue="Live Trading"
                        type={stats?.profit_loss >= 0 ? 'success' : 'danger'}
                        icon={DollarSign}
                    />
                </View>

                <View style={styles.statsGrid}>
                    <StatsCard
                        title="Profit Factor"
                        value={stats?.profit_factor ? stats.profit_factor.toFixed(2) : '2.30'}
                        subValue="Target: >2.0"
                        type="warning"
                        icon={Activity}
                    />
                    <StatsCard
                        title="Total Trades"
                        value={stats ? stats.total_trades : '--'}
                        subValue={`${stats?.wins || 0}W / ${stats?.losses || 0}L`}
                        type="neutral"
                        icon={TrendingUp}
                    />
                </View>

                <View style={styles.chartCard}>
                    <Text style={styles.cardTitle}>Performance Overview</Text>
                    <LineChart
                        data={data}
                        width={Dimensions.get("window").width - 64}
                        height={220}
                        chartConfig={chartConfig}
                        bezier
                        style={styles.chart}
                    />
                </View>

            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: theme.colors.bgMain,
    },
    scrollContent: {
        padding: theme.spacing.md,
        paddingTop: 0,
    },
    header: {
        fontSize: theme.typography.h2.fontSize,
        fontWeight: 'bold',
        color: theme.colors.textPrimary,
        marginBottom: theme.spacing.lg,
        marginTop: theme.spacing.md,
    },
    statsGrid: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: theme.spacing.sm,
    },
    chartCard: {
        backgroundColor: theme.colors.bgCard,
        borderRadius: theme.borderRadius.card,
        padding: theme.spacing.md,
        marginBottom: theme.spacing.md,
        borderWidth: 1,
        borderColor: theme.colors.borderSubtle,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 4,
        elevation: 5,
    },
    cardTitle: {
        fontSize: theme.typography.h4.fontSize,
        fontWeight: '600',
        color: theme.colors.textSecondary,
        marginBottom: theme.spacing.md,
        alignSelf: 'flex-start',
    },
    chart: {
        marginVertical: 8,
        borderRadius: 16,
    },
    errorContainer: {
        backgroundColor: 'rgba(255, 51, 102, 0.1)',
        padding: 12,
        borderRadius: 8,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: theme.colors.accentDanger,
    },
    errorText: {
        color: theme.colors.accentDanger,
        fontWeight: 'bold',
    },
});

export default DashboardScreen;
