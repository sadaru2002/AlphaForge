import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import client from '../api/client';
import { theme } from '../theme';

const LiveTicker = () => {
  const [prices, setPrices] = useState({});

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await client.get('/api/prices/live');
        setPrices(response.data.prices || {});
      } catch (error) {
        // Silent fail for ticker
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {Object.entries(prices).map(([symbol, data]) => (
          <View key={symbol} style={styles.tickerItem}>
            <Text style={styles.symbol}>{symbol.replace('_', '')}</Text>
            <Text style={styles.price}>{data.bid?.toFixed(5) || '--'}</Text>
            <Text style={styles.change}>●</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 50,
    backgroundColor: theme.colors.bgMain,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.borderSubtle,
    marginBottom: theme.spacing.md,
  },
  tickerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    height: '100%',
    borderRightWidth: 1,
    borderRightColor: theme.colors.borderSubtle,
  },
  symbol: {
    color: theme.colors.textPrimary,
    fontWeight: 'bold',
    marginRight: theme.spacing.sm,
  },
  price: {
    color: theme.colors.textSecondary,
    fontFamily: 'monospace',
    marginRight: theme.spacing.sm,
  },
  change: {
    fontSize: 10,
    color: theme.colors.accentPrimary,
  },
});

export default LiveTicker;
