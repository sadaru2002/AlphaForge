export const theme = {
    colors: {
        // Background Colors
        bgMain: '#0A0E1A',           // Deep Navy Black
        bgCard: '#131825',            // Slightly lighter navy
        bgElevated: '#1A1F2E',        // Medium dark blue-gray
        bgHover: '#1F2433',           // Subtle lighter on hover

        // Accent Colors
        accentPrimary: '#7FFF00',     // Electric Lime Green
        accentSuccess: '#00FF87',     // Spring Green
        accentWarning: '#FFB800',     // Vibrant Amber
        accentDanger: '#FF3366',      // Hot Pink Red
        accentInfo: '#00D9FF',        // Cyan Blue

        // Text Colors
        textPrimary: '#FFFFFF',       // Pure White
        textSecondary: '#A0AEC0',     // Cool Gray
        textMuted: '#718096',         // Darker Gray
        textDisabled: '#4A5568',      // Very Dark Gray

        // Border Colors
        borderSubtle: '#1E293B',      // Dark slate
        borderElevated: '#334155',    // Medium slate
        borderActive: '#7FFF00',      // Electric Lime
    },
    borderRadius: {
        card: 16,
        button: 8,
        input: 6,
        badge: 12,
    },
    spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
    },
    typography: {
        h1: { fontSize: 36, lineHeight: 42, fontWeight: '700' },
        h2: { fontSize: 28, lineHeight: 34, fontWeight: '700' },
        h3: { fontSize: 22, lineHeight: 28, fontWeight: '600' },
        body: { fontSize: 14, lineHeight: 21 },
        small: { fontSize: 12, lineHeight: 18 },
        tiny: { fontSize: 10, lineHeight: 14, fontWeight: '500' },
    }
};
