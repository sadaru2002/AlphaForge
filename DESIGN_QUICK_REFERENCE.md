# AlphaForge Design System Quick Reference

## 🎨 Color Palette

### Backgrounds
```css
bg-bg-main       → #0A0E1A (Deep Navy)
bg-bg-card       → #131825 (Card Background)
bg-bg-elevated   → #1A1F2E (Elevated Card)
bg-bg-hover      → #1F2433 (Hover State)
```

### Accents
```css
accent-primary   → #7FFF00 (Electric Lime - Buy/Success)
accent-success   → #00FF87 (Spring Green - Positive)
accent-warning   → #FFB800 (Amber - Warning)
accent-danger    → #FF3366 (Hot Pink - Sell/Loss)
accent-info      → #00D9FF (Cyan - Info)
```

### Text
```css
text-text-primary    → #FFFFFF (White)
text-text-secondary  → #A0AEC0 (Cool Gray)
text-text-muted      → #718096 (Dark Gray)
text-text-disabled   → #4A5568 (Very Dark)
```

### Borders
```css
border-border-subtle   → #1E293B (Subtle)
border-border-elevated → #334155 (Medium)
border-border-active   → #7FFF00 (Active)
```

## 📏 Typography

### Font Families
```css
font-sans  → Inter, system-ui
font-mono  → JetBrains Mono, Fira Code
```

### Font Sizes
```css
text-h1      → 36px / 700 weight
text-h2      → 28px / 700 weight
text-h3      → 22px / 600 weight
text-h4      → 18px / 600 weight
text-body-lg → 16px / 400 weight
text-body    → 14px / 400 weight
text-small   → 12px / 400 weight
text-tiny    → 10px / 500 weight
```

## 🎯 Component Classes

### Cards
```css
.card              /* Base card */
.card-hover        /* With lift on hover */
```

### Buttons
```css
.btn-primary       /* Green CTA */
.btn-secondary     /* Outlined */
.btn-danger        /* Red danger */
```

### Badges
```css
.badge             /* Base badge */
.badge-success     /* Green */
.badge-warning     /* Amber */
.badge-danger      /* Red */
.badge-info        /* Cyan */
.badge-neutral     /* Gray */
```

### Signals
```css
.signal-buy        /* Green left border */
.signal-sell       /* Red left border */
.signal-neutral    /* Gray left border */
```

### Special Effects
```css
.live-indicator    /* Blinking dot */
.text-gradient-green /* Green gradient */
.glass             /* Glassmorphism */
.shimmer           /* Loading effect */
```

## 📐 Spacing Scale (8px base)

```css
p-1  → 4px
p-2  → 8px   (base unit)
p-3  → 12px
p-4  → 16px
p-6  → 24px
p-8  → 32px
p-12 → 48px
```

## 🔲 Border Radius

```css
rounded-card    → 16px (cards)
rounded-button  → 8px  (buttons)
rounded-input   → 6px  (inputs)
rounded-badge   → 12px (badges)
```

## ✨ Shadows

```css
shadow-card        /* Card elevation */
shadow-card-hover  /* Lifted + green glow */
shadow-button      /* Button elevation */
shadow-focus       /* Focus ring */
```

## 🎬 Animations

```css
animate-pulse-green  /* Green pulse (2s) */
animate-shimmer      /* Loading shimmer (1.5s) */
transition-smooth    /* Standard transition */
```

## 📱 Breakpoints

```css
sm   → 640px   (mobile landscape)
md   → 768px   (tablet)
lg   → 1024px  (laptop)
xl   → 1280px  (desktop)
2xl  → 1536px  (large desktop)
```

## 🎨 Usage Examples

### KPI Card
```jsx
<div className="card card-hover p-6">
  <h3 className="text-body text-text-secondary mb-2">Win Rate</h3>
  <p className="text-h1 font-bold text-text-primary">72.5%</p>
  <span className="text-small text-accent-success">↗ +12.5%</span>
</div>
```

### Signal Card
```jsx
<div className="card signal-buy p-6">
  <div className="live-indicator mb-4">
    <div className="live-dot"></div>
    <span className="text-tiny text-accent-danger">LIVE</span>
  </div>
  <h3 className="text-h2 text-accent-primary">BUY XAUUSD</h3>
  <span className="badge badge-success">95% Confidence</span>
</div>
```

### Button
```jsx
<button className="btn-primary">
  Execute Trade
</button>
```

### Live Price
```jsx
<div className="text-h2 font-mono text-accent-primary">
  2649.50
</div>
```

## 🎯 Color Usage Rules

### ✅ DO
- Use `accent-primary` for buy signals, success, CTAs
- Use `accent-danger` for sell signals, losses, errors
- Use `accent-info` for neutral information
- Use `accent-warning` for cautions, pending states
- Use `text-secondary` for labels, descriptions
- Use `text-muted` for timestamps, helpers

### ❌ DON'T
- Mix conflicting accent colors on same element
- Use bright colors for body text (readability)
- Ignore contrast ratios (accessibility)
- Overuse animations (performance)

## ♿ Accessibility

### Focus States
```css
.focus-visible:focus-visible {
  @apply outline-none ring-2 ring-accent-primary;
}
```

### Min Touch Targets
- Buttons: 48px height minimum
- Interactive elements: 44px minimum

### Contrast Ratios
- Body text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum

## 🚀 Performance Tips

1. **Use CSS Animations**: Faster than JS
2. **Limit Shadows**: Performance impact
3. **Optimize Images**: WebP format
4. **Lazy Load**: Below-fold components
5. **Debounce**: Scroll/resize events

## 💡 Pro Tips

1. **Consistent Spacing**: Always use spacing scale
2. **Color Tokens**: Use design tokens, not raw hex
3. **Hover States**: All interactive elements need them
4. **Loading States**: Show feedback on async actions
5. **Mobile First**: Design for mobile, enhance for desktop

---

**Quick Copy-Paste Snippets**

```jsx
// Card
<div className="card card-hover p-6">Content</div>

// Button
<button className="btn-primary">Click Me</button>

// Badge
<span className="badge badge-success">Active</span>

// Live Indicator
<div className="live-indicator">
  <div className="live-dot"></div>
  <span className="text-tiny">LIVE</span>
</div>

// Gradient Text
<h1 className="text-h1 text-gradient-green">AlphaForge</h1>

// Signal Card Header
<div className="flex items-center gap-2">
  <span className="text-h2 text-accent-primary">BUY</span>
  <span className="badge badge-success">95%</span>
</div>
```

---

**Made for AlphaForge Gemini Pro Trading System**
