import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../theme';

const StatsCard = ({ title, value, subValue, type, icon: IconName }) => {
    const getColors = () => {
        switch (type) {
            case 'success': return { text: theme.colors.accentSuccess, border: theme.colors.accentSuccess, bg: theme.colors.bgCard };
            case 'warning': return { text: theme.colors.accentWarning, border: theme.colors.accentWarning, bg: theme.colors.bgCard };
            case 'danger': return { text: theme.colors.accentDanger, border: theme.colors.accentDanger, bg: theme.colors.bgCard };
            default: return { text: theme.colors.textMuted, border: theme.colors.borderSubtle, bg: theme.colors.bgCard };
        }
    };

    const colors = getColors();

    return (
        <View style={[styles.card, { borderLeftColor: colors.border }]}>
            <View style={styles.header}>
                <Text style={styles.title}>{title}</Text>
                {IconName && <IconName size={24} color={colors.text} />}
            </View>
            <Text style={styles.value}>{value}</Text>
            {subValue && <Text style={[styles.subValue, { color: colors.text }]}>{subValue}</Text>}

            {/* Decorative gradient overlay effect (simulated with opacity) */}
            <View style={[styles.overlay, { backgroundColor: colors.text }]} />
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: theme.colors.bgCard,
        borderRadius: theme.borderRadius.card,
        padding: theme.spacing.md,
        borderWidth: 1,
        borderColor: theme.colors.borderSubtle,
        borderLeftWidth: 4,
        marginBottom: 12,
        flex: 1,
        minWidth: '45%',
        marginHorizontal: 4,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 4,
        elevation: 5,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: theme.spacing.sm,
    },
    title: {
        color: theme.colors.textSecondary,
        fontSize: theme.typography.body.fontSize,
        fontWeight: '500',
    },
    value: {
        color: theme.colors.textPrimary,
        fontSize: 28, // Larger for impact
        fontWeight: 'bold',
        marginBottom: theme.spacing.xs,
    },
    subValue: {
        fontSize: theme.typography.small.fontSize,
        fontWeight: '500',
    },
    overlay: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 2,
        opacity: 0.5,
    },
});

export default StatsCard;
