# AlphaForge Signal Generation Guide

## Quick Start

### Generate Signals for Yesterday's Data

```bash
cd backend
python generate_yesterday_signals.py
```

This will:
- Fetch real OANDA data from yesterday
- Analyze GBP_USD, XAU_USD, and USD_JPY
- Generate signals at hourly intervals
- Store signals in the database
- Display summary of generated signals

---

## Generate Signals for Any Date

```bash
cd backend
python run_date_signals.py [YYYY-MM-DD]
```

**Examples:**
```bash
# Generate signals for November 20, 2025
python run_date_signals.py 2025-11-20

# Generate signals for a week ago
python run_date_signals.py 2025-11-14

# Default to yesterday if no date provided
python run_date_signals.py
```

---

## Check Signals in Database

```bash
cd backend
python check_signals.py
```

This shows:
- Total signals in database
- Yesterday's signals
- Latest 10 signals with details

---

## Verify System is Working

### 1. Start Backend Server

```bash
cd backend
python app.py
```

Server will run on: http://localhost:5000

### 2. Test API

```bash
cd backend
python test_api_signals.py
```

This verifies the `/signals` endpoint is returning data correctly.

### 3. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

### 4. View Signals

Open browser and navigate to:
- Homepage: http://localhost:3000
- Signals page: http://localhost:3000/signals

---

## Clean Up Old Data

```bash
cd backend
python cleanup_old_data.py
```

This will:
- Remove duplicate database files
- Clear old log files
- Archive everything before deletion
- Keep main database: `backend/trading_signals.db`

---

## Database Management

### View Database Contents

```bash
cd backend
python check_db_simple.py
```

### Database Location

Main database: `backend/trading_signals.db`

### Database Schema

**trading_signals** table:
- id, timestamp, symbol, direction
- entry, stop_loss, tp1, tp2, tp3
- confidence_score, signal_strength
- market_condition, regime
- status, outcome, actual_pnl
- And more...

---

## Workflow

### Daily Signal Generation

1. **Generate yesterday's signals:**
   ```bash
   python generate_yesterday_signals.py
   ```

2. **Check results:**
   ```bash
   python check_signals.py
   ```

3. **Start servers (if not running):**
   ```bash
   # Terminal 1: Backend
   python app.py
   
   # Terminal 2: Frontend
   cd ../frontend
   npm run dev
   ```

4. **View signals in browser:**
   - Navigate to http://localhost:3000/signals

---

## Understanding Signal Quality

### Signal Strength
- **STRONG**: Confidence ≥ 70%
- **MEDIUM**: Confidence 50-69%
- **WEAK**: Confidence < 50%

### Market Regime
- **TRENDING**: Strong directional movement
- **RANGING**: Sideways market
- **VOLATILE**: High volatility detected
- **UNKNOWN**: Regime not clearly defined

### Signal Status
- **PENDING**: Signal generated, awaiting action
- **ACTIVE**: Trade is active
- **CLOSED**: Trade completed
- **EXPIRED**: Signal expired without entry
- **CANCELLED**: Signal cancelled

---

## Troubleshooting

### No Signals Generated

This is normal! The AlphaForge system has strict quality filters:
- Multi-timeframe agreement required
- Regime must be tradeable
- Confidence threshold must be met
- Risk/reward ratio must be favorable

**Not every day will have signals** - this protects your capital.

### Database Issues

If you see database errors:
1. Check `backend/trading_signals.db` exists
2. Run `python cleanup_old_data.py` to clean duplicates
3. Delete the database and restart the system (signals will be lost)

### API Not Working

1. Ensure backend is running: `python app.py`
2. Test endpoint: `python test_api_signals.py`
3. Check port 5000 is not in use by another process

### Frontend Not Displaying Signals

1. Check backend is running on port 5000
2. Check frontend is running on port 3000
3. Clear browser cache and refresh
4. Check browser console for errors (F12)

---

## System Architecture

```
AlphaForge/
├── backend/
│   ├── app.py                          # FastAPI server
│   ├── generate_yesterday_signals.py   # Generate yesterday's signals
│   ├── run_date_signals.py            # Generate signals for any date
│   ├── enhanced_signal_generator.py    # Signal generation engine
│   ├── check_signals.py               # View signals in DB
│   ├── check_db_simple.py             # Simple DB query
│   ├── test_api_signals.py            # Test API endpoint
│   ├── cleanup_old_data.py            # Clean old files
│   ├── trading_signals.db             # Main database
│   └── database/
│       ├── signal_models.py           # Database models
│       └── signal_crud.py             # Database operations
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   └── Signals.jsx            # Signals page
    │   └── services/
    │       └── api.js                 # API service
    └── package.json
```

---

## Next Steps

1. **Backtest the strategy** to validate performance
2. **Set up automated scheduling** to run signals daily
3. **Connect to live trading** (manual execution recommended)
4. **Monitor and journal trades** using the Journal page

---

## Support

For issues or questions:
1. Check this README
2. Review the walkthrough document
3. Check the ALPHAFORGE_*.md documentation files

---

**Last Updated:** 2025-11-21
**System Status:** ✅ Operational
