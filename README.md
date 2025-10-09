# 📊 AlphaForge Frontend Dashboard

Modern React dashboard for the AlphaForge Trading Bot.

## Features

- 📈 Real-time signal display
- 📊 Live TradingView charts
- 📉 Performance analytics
- 🔄 Auto-refresh every 5 seconds
- 📱 Responsive design
- 🎨 Modern dark theme with Tailwind CSS

## Tech Stack

- **React 18** - UI framework
- **Recharts** - Chart visualization
- **Axios** - API communication
- **Tailwind CSS** - Styling
- **Moment.js** - Date formatting

## Quick Start

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm start
```

Opens at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── index.js            # Entry point
│   ├── App.jsx             # Main component
│   ├── App.css             # App styles
│   ├── index.css           # Global styles
│   └── components/
│       ├── Dashboard.jsx   # Performance overview
│       ├── SignalCard.jsx  # Signal display
│       ├── Chart.jsx       # TradingView widget
│       └── Stats.jsx       # Statistics cards
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind config
└── postcss.config.js       # PostCSS config
```

## Components

### App.jsx
Main application component that:
- Fetches data from backend API
- Manages application state
- Handles auto-refresh
- Renders all child components

### Dashboard.jsx
Performance overview with:
- Signal history chart
- Detailed statistics table
- Win rate tracking

### SignalCard.jsx
Individual signal display showing:
- Direction (BUY/SELL)
- Entry price
- Stop loss
- Take profit levels (TP1, TP2)
- Setup type
- ML confidence
- Confirmations score

### Chart.jsx
Live chart component:
- TradingView widget integration
- Real-time GBP/USD data
- 5-minute timeframe

### Stats.jsx
Statistics cards for:
- Win rate
- Profit factor
- Net profit
- Today's signals count

## API Integration

### Endpoints Used

```javascript
GET /api/signals/latest  // Get recent signals
GET /api/stats           // Get performance stats
GET /api/status          // Get bot status
GET /api/health          // Health check
```

### Data Flow

1. App.jsx fetches data every 5 seconds
2. Updates state with new signals/stats
3. Components re-render with new data
4. User sees updated information

## Styling

### Tailwind CSS Classes

Common classes used:
- `bg-gray-800` - Dark background
- `text-blue-400` - Accent color
- `rounded-lg` - Rounded corners
- `p-4` - Padding
- `hover:bg-gray-750` - Hover effects

### Color Scheme

- Background: Gray-900 (#111827)
- Cards: Gray-800 (#1F2937)
- Text: White/Gray-400
- Accent: Blue-400
- Success: Green-400
- Error: Red-400

## Configuration

### API Base URL

Located in `App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

Change this if backend runs on different port.

### Auto-Refresh Interval

Located in `App.jsx`:

```javascript
const interval = setInterval(fetchData, 5000); // 5 seconds
```

Adjust the `5000` value (milliseconds) to change refresh rate.

## Customization

### Adding New Components

1. Create component in `src/components/`
2. Import in `App.jsx`
3. Add to render method

Example:
```jsx
import NewComponent from './components/NewComponent';

// In render:
<NewComponent data={myData} />
```

### Changing Theme

Edit `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#your-color',
      }
    },
  },
}
```

## Development

### Running Tests

```bash
npm test
```

### Linting

```bash
npm run lint
```

### Building

```bash
npm run build
```

Creates optimized production build in `build/` directory.

## Deployment

### Option 1: Static Hosting

```bash
npm run build
# Upload build/ folder to Netlify/Vercel/GitHub Pages
```

### Option 2: Docker

```dockerfile
FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Option 3: Nginx

```bash
npm run build
# Copy build/ to nginx html directory
sudo cp -r build/* /var/www/html/
```

## Troubleshooting

### "Module not found"
```bash
npm install
```

### "Port 3000 already in use"
```bash
# Kill process on port 3000
npx kill-port 3000
```

### "Failed to fetch from API"
- Check backend is running on port 5000
- Verify CORS is enabled in backend
- Check API_BASE_URL in App.jsx

### "Dashboard blank"
- Open browser console (F12)
- Check for JavaScript errors
- Verify backend API is responding
- Test: `http://localhost:5000/api/health`

## Performance

- **Initial Load:** ~2 seconds
- **Refresh Rate:** 5 seconds
- **Bundle Size:** ~500 KB (gzipped)
- **Memory Usage:** ~50-100 MB

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Part of the AlphaForge Trading Bot system.

## Support

See main README.md in project root for full documentation.
