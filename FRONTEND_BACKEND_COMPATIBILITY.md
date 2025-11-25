# 🔗 Frontend-Backend Compatibility Guide

## ✅ System Status: FULLY COMPATIBLE

**Frontend**: Running on `http://localhost:3000` ✅  
**Backend**: Running on `http://localhost:5000` ✅  
**Scheduler**: Running (5-minute cycles) ✅

---

## 🔧 Configuration Changes Made

### 1. Frontend API Configuration
**File**: `frontend/src/config/api.js`

```javascript
// Updated to use local backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

**Before**: Pointed to VPS (161.118.218.33:5000)  
**After**: Points to localhost:5000 (your local backend)

---

## 🌐 API Endpoints - Complete Compatibility

### ✅ Signals Endpoints

| Frontend Request | Backend Endpoint | Status |
|-----------------|------------------|--------|
| `GET /api/signals/today` | `GET /api/signals/today` | ✅ Added |
| `POST /api/signals/generate` | `POST /api/signals/generate` | ✅ Exists |
| `POST /api/signals/enhanced/generate` | `POST /api/signals/enhanced/generate` | ✅ Exists |
| `GET /api/signals` | `GET /api/signals` | ✅ Exists |
| `GET /api/signals/active` | `GET /api/signals/active` | ✅ Exists |
| `GET /api/signals/statistics` | `GET /api/signals/statistics` | ✅ Exists |
| `GET /api/signals/performance` | `GET /api/signals/performance` | ✅ Exists |

### ✅ Journal Endpoints

| Frontend Request | Backend Endpoint | Status |
|-----------------|------------------|--------|
| `GET /api/journal/entries` | `GET /api/journal/entries` | ✅ Exists |
| `POST /api/journal/entries` | `POST /api/journal/entries` | ✅ Exists |
| `GET /api/journal/entries/{id}` | `GET /api/journal/entries/{entry_id}` | ✅ Exists |
| `PUT /api/journal/entries/{id}` | `PUT /api/journal/entries/{entry_id}` | ✅ Exists |
| `DELETE /api/journal/entries/{id}` | `DELETE /api/journal/entries/{entry_id}` | ✅ Exists |
| `GET /api/journal/statistics` | `GET /api/journal/statistics` | ✅ Exists |

### ✅ Additional Endpoints

| Frontend Request | Backend Endpoint | Status |
|-----------------|------------------|--------|
| `GET /health` | `GET /health` | ✅ Exists |
| `GET /api/status` | `GET /api/status` | ✅ Exists |
| `GET /api/stats` | `GET /api/stats` | ✅ Exists |
| `POST /api/strategy/start` | `POST /api/strategy/start` | ✅ Exists |
| `POST /api/strategy/stop` | `POST /api/strategy/stop` | ✅ Exists |
| `GET /api/prices/live/{symbol}` | `GET /api/prices/live/{symbol}` | ✅ Exists |
| `GET /api/symbols` | `GET /api/symbols` | ✅ Exists |

---

## 🎯 How to Access

### Frontend Dashboard
1. Open browser: **http://localhost:3000**
2. Features available:
   - ✅ Signal cards and table
   - ✅ Trading journal
   - ✅ Analytics dashboard
   - ✅ Live price ticker
   - ✅ Signal generation buttons
   - ✅ Win rate statistics
   - ✅ Performance metrics

### Backend API
- **Base URL**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **API Docs**: http://localhost:5000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:5000/redoc

---

## 📊 Complete Workflow (Frontend ↔ Backend)

### 1. **Automated Signal Generation** (Every 5 Minutes)
```
Scheduler → POST /api/signals/enhanced/generate
         ↓
Backend analyzes M5/M15/H1
         ↓
Saves to database
         ↓
Frontend polls: GET /api/signals/today
         ↓
Displays in signal cards & table
```

### 2. **Manual Signal Generation** (User Clicks Button)
```
Frontend → POST /api/signals/generate
        ↓
Backend generates signal
        ↓
Returns signal data
        ↓
Frontend updates UI
```

### 3. **Trading Journal Workflow**
```
User trades signal → Frontend POST /api/journal/entries
                  ↓
Backend saves to database
                  ↓
Frontend GET /api/journal/entries
                  ↓
Display in journal table
                  ↓
Frontend GET /api/journal/statistics
                  ↓
Calculate & display win rate
```

### 4. **Analytics Dashboard**
```
Frontend GET /api/journal/statistics
        ↓
Backend calculates:
  - Win rate overall
  - Win rate by pair
  - Win rate by regime
  - Total PnL
  - Profit factor
        ↓
Frontend displays charts & metrics
```

---

## 🔄 CORS Configuration

**Backend CORS Settings** (app.py):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows frontend on localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Status**: ✅ Frontend can make requests to backend without CORS errors

---

## 🗄️ Database Integration

### Tables Used:
1. **trading_signals** - Stores generated signals
2. **journal_entries** - Stores manual trades & outcomes

### Signal Flow:
```
Scheduler/Manual Generate
    ↓
Signal Saved to DB (trading_signals table)
    ↓
Frontend fetches via API
    ↓
User trades signal
    ↓
Journal entry saved (journal_entries table)
    ↓
Analytics calculated from journal
```

---

## 🎯 Key Features Working

### ✅ Signal Generation
- **Automated**: Every 5 minutes via scheduler
- **Manual**: Click "Generate Signal" button in frontend
- **Multi-timeframe**: M5, M15, H1 analysis
- **AI Validation**: Gemini API (when configured)

### ✅ Signal Display
- **Signal Cards**: Visual cards for each signal
- **Signal Table**: Tabular view with sorting
- **Real-time Updates**: Polls backend every 30 seconds
- **Today's Signals**: Filtered view of current day

### ✅ Trading Journal
- **Add Trades**: Manual entry of trades
- **Track Outcomes**: Win/Loss, PnL, notes
- **Edit/Delete**: Full CRUD operations
- **Statistics**: Automatic win rate calculation

### ✅ Analytics
- **Win Rate**: Overall and by pair
- **Regime Performance**: Win rate by market regime
- **PnL Tracking**: Total profit/loss
- **Profit Factor**: Risk/reward metrics

---

## 🚀 Quick Start Commands

### Terminal 1: Backend
```bash
cd backend
python app.py
```

### Terminal 2: Scheduler
```bash
cd backend
python signal_scheduler.py
```

### Terminal 3: Frontend
```bash
cd frontend
npm start
```

### All-in-One (Alternative)
```bash
python start_system.py  # Starts backend + scheduler
cd frontend ; npm start  # Start frontend separately
```

---

## 🔍 Testing the Integration

### 1. Test Backend Health
```bash
# Open browser or curl
http://localhost:5000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T00:30:00"
}
```

### 2. Test Signal Generation
```bash
# From frontend: Click "Generate Signal" button
# Or via API:
curl -X POST http://localhost:5000/api/signals/generate
```

### 3. Test Journal Entry
```bash
# From frontend: Go to Journal page → Add Trade
# Or via API:
curl -X POST http://localhost:5000/api/journal/entries \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "GBP_USD",
    "signal_type": "BUY",
    "entry_price": 1.2500,
    "outcome": "win",
    "pnl": 50.0
  }'
```

### 4. Test Today's Signals
```bash
# From frontend: Dashboard automatically fetches
# Or via API:
curl http://localhost:5000/api/signals/today
```

---

## 📱 Frontend Pages Available

1. **Dashboard** (`/`) - Signal cards, live prices, quick stats
2. **Signals** (`/signals`) - Signal table with filters
3. **Journal** (`/journal`) - Trading journal with CRUD
4. **Analytics** (`/analytics`) - Win rate, performance charts
5. **Complete Platform** (`/complete`) - All-in-one view

---

## 🎨 UI Components Working

### Signal Cards
```jsx
<SignalCard 
  pair="GBP_USD"
  signal="BUY"
  confidence={0.85}
  entry={1.2500}
  stopLoss={1.2450}
  takeProfit={1.2600}
/>
```

### Signals Table
```jsx
<SignalsTable 
  signals={todaySignals}
  onTrade={handleTrade}
/>
```

### Journal Entry Form
```jsx
<JournalForm 
  onSubmit={addJournalEntry}
  pairs={['GBP_USD', 'XAU_USD', 'USD_JPY']}
/>
```

---

## 🔧 Environment Variables

### Frontend (.env - optional)
```env
REACT_APP_API_URL=http://localhost:5000
```

### Backend (.env - required)
```env
OANDA_ACCOUNT_ID=your_account_id
OANDA_ACCESS_TOKEN=your_access_token
OANDA_ENVIRONMENT=practice
GEMINI_API_KEY=your_gemini_key  # Optional
```

---

## ✅ Compatibility Checklist

- [x] Frontend connects to backend on localhost:5000
- [x] CORS enabled for cross-origin requests
- [x] All signal endpoints working
- [x] All journal endpoints working
- [x] Today's signals endpoint added
- [x] Database integration functional
- [x] Automated scheduler running
- [x] Real-time signal generation
- [x] Manual signal generation
- [x] Journal CRUD operations
- [x] Statistics & analytics
- [x] Win rate calculation
- [x] Multi-timeframe analysis
- [x] Regime detection
- [x] Quality filters

---

## 🎉 System Status: PRODUCTION READY!

**Frontend**: ✅ Running on port 3000  
**Backend**: ✅ Running on port 5000  
**Scheduler**: ✅ Analyzing every 5 minutes  
**Database**: ✅ SQLite/PostgreSQL ready  
**CORS**: ✅ Enabled  
**API**: ✅ All endpoints compatible  

**You can now:**
1. View automated signals in the frontend dashboard
2. Generate signals manually via UI buttons
3. Add trades to your journal
4. Track win rate and analytics
5. Monitor live prices
6. See real-time signal updates

---

**Last Updated**: November 13, 2025  
**System**: AlphaForge v1.0  
**Status**: ✅ FULLY OPERATIONAL
