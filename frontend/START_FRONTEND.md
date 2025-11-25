# Starting the AlphaForge Frontend

## Quick Start

### Method 1: Using npm start (Recommended)
```bash
cd frontend
npm start
```

### Method 2: Using npm run dev
```bash
cd frontend
npm run dev
```

## Server Information

- **URL**: http://localhost:3000
- **Backend API**: http://localhost:5000 (configured automatically)
- **Auto-reload**: Enabled (changes auto-refresh browser)

## First Time Setup

If you haven't installed dependencies:

```bash
cd frontend
npm install
```

This will install all required packages from `package.json`.

## Verification

Once started, the frontend will:
1. Compile React application
2. Open browser automatically at http://localhost:3000
3. Connect to backend at http://localhost:5000

### Check if Frontend is Running

```bash
# In PowerShell
Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing

# Or open browser to:
# http://localhost:3000
```

## Development Features

- ✅ Hot Module Replacement (HMR) - Changes reflect instantly
- ✅ Error overlay in browser
- ✅ Source maps for debugging
- ✅ Fast refresh for React components

## Configuration

### API Configuration

The frontend automatically connects to:
- **Development**: http://localhost:5000
- **Production**: http://161.118.218.33:5000

Configured in `src/config/api.js`:
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://161.118.218.33:5000'
  : 'http://localhost:5000';
```

### Port Configuration

Default port is **3000**. To change it:

1. Set environment variable:
```bash
# Windows PowerShell
$env:PORT=3001; npm start

# Or create .env file in frontend directory:
PORT=3001
```

## Troubleshooting

### Port Already in Use
If port 3000 is already in use:
```bash
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
$env:PORT=3001; npm start
```

### Dependencies Not Installed
```bash
cd frontend
npm install
```

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend Connection Issues
1. Ensure backend is running on http://localhost:5000
2. Check CORS settings in backend `app.py`
3. Verify API configuration in `src/config/api.js`

### Module Not Found Errors
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules
npm install
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run dev` - Alias for npm start

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── config/         # Configuration files
│   └── utils/          # Utility functions
├── public/             # Static files
└── package.json        # Dependencies
```

## Features

### Main Pages
- **Dashboard** - Overview and statistics
- **Signals** - Trading signals management
- **Journal** - Trade journal entries
- **Analytics** - Performance analytics
- **Backtesting** - Strategy backtesting
- **Settings** - Configuration

### Components
- Signal cards and tables
- Live price tickers
- Charts and graphs
- Calendar heatmap
- Real-time updates

## Production Build

To build for production:

```bash
cd frontend
npm run build
```

This creates an optimized build in the `build/` directory.

## Status

✅ **Frontend server is starting!**

The React development server typically takes 30-60 seconds to compile and start.

Once ready, it will:
- Open automatically in your browser
- Be available at http://localhost:3000
- Connect to backend at http://localhost:5000

## Next Steps

1. ✅ Frontend is starting
2. Wait for compilation (30-60 seconds)
3. Browser will open automatically
4. Start using the AlphaForge platform!

## Full Stack Status

- ✅ **Backend**: Running on http://localhost:5000
- ✅ **Frontend**: Starting on http://localhost:3000
- ✅ **Database**: Connected
- ✅ **API**: Fully functional

**Your AlphaForge trading platform is ready!** 🚀


