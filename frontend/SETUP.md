# AlphaForge Frontend - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm start
```

The application will open at `http://localhost:3000`

### 3. Ensure Backend is Running
The frontend requires the backend server to be running on port 5001.

```bash
# In the backend directory
python app.py
```

## What Was Fixed

### ✅ Critical Fixes Applied

1. **Created package.json** - Added all required dependencies:
   - React 18 & React Router v6
   - Chart.js & Recharts for visualizations
   - AG Grid for data tables
   - Lucide React for icons
   - All other necessary packages

2. **Created public/index.html** - React app entry point

3. **Fixed App.jsx Import Error** - Corrected multi-line import statement

4. **Fixed API Endpoints** - Changed port 5000 to 5001 in Journal.jsx

5. **Added Missing Routes** - Added Backtesting and Settings routes to App.jsx

6. **Created Configuration Files**:
   - `.gitignore` for version control
   - `README.md` for documentation
   - `SETUP.md` (this file)

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML entry point
├── components/             # Reusable UI components
│   ├── Dashboard.jsx       # Main dashboard
│   ├── Chart.jsx           # TradingView chart
│   ├── Stats.jsx           # Statistics cards
│   ├── Navbar.jsx          # Navigation bar
│   ├── Sidebar.jsx         # Side navigation
│   ├── Toasts.jsx          # Toast notifications
│   ├── LivePriceTicker.jsx # Real-time price display
│   └── TradingViewWidget.jsx # TradingView integration
├── pages/                  # Page components
│   ├── Analytics.jsx       # Performance analytics
│   ├── Backtesting.jsx     # Strategy backtesting
│   ├── Journal.jsx         # Trading journal
│   ├── Settings.jsx        # System settings
│   └── Signals.jsx         # Trading signals
├── services/
│   └── api.js              # API service layer
├── App.jsx                 # Main app component
├── index.js                # Entry point
├── package.json            # Dependencies
└── README.md               # Documentation
```

## Available Routes

- `/` - Dashboard (overview with stats and charts)
- `/signals` - Trading signals page
- `/analytics` - Performance analytics
- `/journal` - Trading journal with detailed logs
- `/backtesting` - Strategy backtesting interface
- `/settings` - System configuration

## Features

### ✨ Implemented Features

- **Real-time Price Ticker** - Live OANDA prices for XAUUSD, GBPUSD, USDJPY
- **Trading Signals** - View and filter all generated signals
- **Performance Analytics** - Charts and metrics for trading performance
- **Trading Journal** - Log trades with screenshots and statistics
- **Backtesting** - Test strategies against historical data
- **Settings** - Configure risk management and API settings
- **Responsive Design** - Works on desktop and mobile

## API Configuration

The frontend connects to the backend at `http://localhost:5001` by default.

To change this, set the `REACT_APP_API_URL` environment variable:

```bash
# .env file
REACT_APP_API_URL=http://your-backend-url:5001
```

## Troubleshooting

### Port Already in Use
If port 3000 is already in use:
```bash
# Windows
set PORT=3001 && npm start

# Linux/Mac
PORT=3001 npm start
```

### Backend Connection Issues
- Ensure backend is running on port 5001
- Check CORS settings in backend
- Verify API endpoints in `services/api.js`

### Missing Dependencies
```bash
npm install --legacy-peer-deps
```

## Development Tips

- Hot reload is enabled by default
- Console logs show API requests and responses
- Check browser DevTools for errors
- Backend must be running for full functionality

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Next Steps

1. Install dependencies: `npm install`
2. Start the app: `npm start`
3. Ensure backend is running on port 5001
4. Navigate to `http://localhost:3000`
5. Check the Dashboard for live data

## Support

For issues or questions, check:
- Browser console for errors
- Backend logs for API issues
- Network tab for failed requests
