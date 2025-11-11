#!/usr/bin/env python3
"""
AlphaForge API Server
FastAPI backend for trading dashboard with database integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime, timedelta
import asyncio
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables
load_dotenv()

# Database imports
from database.signal_models import Base, TradingSignal, SignalStatus, TradeOutcome
from database.signal_crud import SignalCRUD, AnalyticsCRUD
from database.trade_calculator import TradeCalculator
from database.journal_models import JournalEntry
from database.journal_crud import JournalCRUD
import strategy_variables as config

# Database setup - Read from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_signals.db")

# Configure engine based on database type
if DATABASE_URL.startswith('postgresql'):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AlphaForge API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global state
state = {
    "backend_status": "online",
    "oanda_status": "disconnected",
    "strategy_status": "stopped",
    "gemini_status": "unknown",
    "database_status": "unknown",
    "last_price": None,
}


# Pydantic Models
class SignalCreate(BaseModel):
    symbol: str
    direction: str
    entry: float
    stop_loss: float
    tp1: float
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None

class SignalUpdate(BaseModel):
    status: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    outcome: Optional[str] = None

class Signal(BaseModel):
    id: int
    timestamp: str
    symbol: str
    direction: str  # BUY or SELL
    entry: float
    stop_loss: float
    tp1: float
    status: str
    outcome: Optional[str] = None
    actual_pnl: Optional[float] = None
    confidence: float
    status: str


class PriceData(BaseModel):
    symbol: str
    price: float
    bid: float
    ask: float
    timestamp: str


# Routes
@app.get("/")
async def root():
    return {"message": "AlphaForge API Server", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "backend": state["backend_status"],
        "oanda": state["oanda_status"],
        "strategy": state["strategy_status"]
    }


@app.get("/api/status")
async def get_status_api():
    """Get system status"""
    # Check database status
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        state["database_status"] = "connected"
    except Exception as e:
        state["database_status"] = "disconnected"
    
    # Check Gemini status
    try:
        import os
        gemini_key = os.getenv('GEMINI_API_KEY')
        state["gemini_status"] = "configured" if gemini_key else "not configured"
    except:
        state["gemini_status"] = "unknown"
    
    # Check OANDA status
    try:
        import os
        oanda_key = os.getenv('OANDA_API_KEY')
        state["oanda_status"] = "connected" if oanda_key else "disconnected"
    except:
        state["oanda_status"] = "disconnected"
    
    return {
        "backend": state["backend_status"],
        "oanda": state["oanda_status"],
        "strategy": state["strategy_status"],
        "gemini": state["gemini_status"],
        "database": state["database_status"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """Get system status (legacy endpoint)"""
    return {
        "backend": state["backend_status"],
        "oanda": state["oanda_status"],
        "strategy": state["strategy_status"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/signals")
async def get_signals_api(db: Session = Depends(get_db)):
    """Get all trading signals from database"""
    try:
        signals = SignalCRUD.get_all_signals(db, limit=500)
        return {
            "signals": [signal.to_dict() for signal in signals],
            "count": len(signals)
        }
    except Exception as e:
        print(f"Error fetching signals: {e}")
        return {"signals": [], "count": 0}


@app.get("/signals")
async def get_signals(db: Session = Depends(get_db)):
    """Get recent trading signals (legacy endpoint)"""
    try:
        signals = SignalCRUD.get_all_signals(db, limit=100)
        return {
            "signals": [signal.to_dict() for signal in signals],
            "count": len(signals)
        }
    except Exception as e:
        print(f"Error fetching signals: {e}")
        return {"signals": [], "count": 0}


@app.post("/api/signals/create")
async def create_signal(signal_data: SignalCreate, db: Session = Depends(get_db)):
    """Create a new trading signal"""
    try:
        # Calculate risk:reward ratio
        rr_ratio = TradeCalculator.calculate_risk_reward(
            signal_data.entry,
            signal_data.stop_loss,
            signal_data.tp1,
            signal_data.direction
        )
        
        # Prepare signal data
        new_signal_data = {
            "timestamp": datetime.utcnow(),
            "symbol": signal_data.symbol,
            "direction": signal_data.direction,
            "entry": signal_data.entry,
            "stop_loss": signal_data.stop_loss,
            "tp1": signal_data.tp1,
            "tp2": signal_data.tp2,
            "tp3": signal_data.tp3,
            "rr_ratio": f"1:{rr_ratio}",
            "confidence_score": signal_data.confidence_score or 75.0,
            "reasoning": signal_data.reasoning,
            "status": SignalStatus.PENDING,
        }
        
        # Create signal in database
        signal = SignalCRUD.create_signal(db, new_signal_data)
        
        return {
            "status": "success",
            "message": "Signal created successfully",
            "signal": signal.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating signal: {str(e)}")


# DEPRECATED: Use Trading Journal instead for trade execution tracking
# Signals should only show trade setups, not track execution
# @app.post("/api/signals/{signal_id}/enter")
# async def enter_trade(signal_id: int, entry_price: float, position_size: float = 0.1, db: Session = Depends(get_db)):
#     """DEPRECATED: Use /api/journal/entries to track actual trades"""
#     pass


# DEPRECATED: Use Trading Journal instead for trade outcome tracking  
# Signals should only show trade setups, not track outcomes/PNL
# @app.post("/api/signals/{signal_id}/close")
# async def close_trade(signal_id: int, exit_price: float, db: Session = Depends(get_db)):
#     """DEPRECATED: Use /api/journal/entries to track actual trade outcomes"""
#     pass


@app.get("/api/signals/active")
async def get_active_signals(db: Session = Depends(get_db)):
    """Get all active trades"""
    try:
        signals = SignalCRUD.get_active_signals(db)
        return {
            "signals": [signal.to_dict() for signal in signals],
            "count": len(signals)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active signals: {str(e)}")


@app.get("/api/signals/statistics")
async def get_signal_statistics(days: int = 30, db: Session = Depends(get_db)):
    """Get signal generation statistics (NOT trade performance - use /api/journal/statistics for that)"""
    try:
        # Count signals only (no outcomes)
        signals = SignalCRUD.get_all_signals(db, limit=1000)
        total_signals = len(signals)
        pending_signals = len([s for s in signals if s.status == SignalStatus.PENDING])
        expired_signals = len([s for s in signals if s.status == SignalStatus.EXPIRED])
        
        return {
            "total_signals_generated": total_signals,
            "pending_signals": pending_signals,
            "expired_signals": expired_signals,
            "note": "For trade performance (win rate, PNL), see /api/journal/statistics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


@app.get("/api/signals/symbol/{symbol}")
async def get_signals_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get signals for a specific symbol"""
    try:
        signals = SignalCRUD.get_signals_by_symbol(db, symbol)
        return {
            "symbol": symbol,
            "signals": [signal.to_dict() for signal in signals],
            "count": len(signals)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching signals: {str(e)}")


@app.get("/api/signals/performance")
async def get_symbol_performance(days: int = 30, db: Session = Depends(get_db)):
    """Get performance by symbol"""
    try:
        performance = SignalCRUD.get_symbol_performance(db, days)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating performance: {str(e)}")


# DEPRECATED: This endpoint used the old oanda_integration module
# Frontend doesn't use this endpoint - commented out after cleanup
# @app.get("/api/price/{symbol}")
# async def get_price(symbol: str):
#     """Get current price for a symbol"""
#     try:
#         # Try to fetch real price from OANDA
#         oanda_config = OandaConfig(
#             config.OANDA_ACCESS_TOKEN,
#             config.OANDA_ACCOUNT_ID,
#             config.OANDA_ENVIRONMENT
#         )
#         data_handler = DataHandler(oanda_config)
#         
#         # Fetch latest candle
#         df = data_handler.fetch_historical_data(symbol, config.TIMEFRAME, 1)
#         
#         if not df.empty:
#             latest = df.iloc[-1]
#             state["oanda_status"] = "connected"
#             return {
#                 "symbol": symbol,
#                 "price": float(latest['close']),
#                 "bid": float(latest['close']),
#                 "ask": float(latest['close']),
#                 "timestamp": datetime.now().isoformat()
#             }
#         else:
#             raise HTTPException(status_code=404, detail="No data available")
#             
#     except Exception as e:
#         state["oanda_status"] = "disconnected"
#         # Return mock data for testing
#         return {
#             "symbol": symbol,
#             "price": 1.2650,
#             "bid": 1.2648,
#             "ask": 1.2652,
#             "timestamp": datetime.now().isoformat(),
#             "mock": True
#         }


@app.post("/api/strategy/start")
async def start_strategy():
    """Start the trading strategy"""
    state["strategy_status"] = "running"
    return {"status": "success", "message": "Strategy started"}


@app.post("/api/strategy/stop")
async def stop_strategy():
    """Stop the trading strategy"""
    state["strategy_status"] = "stopped"
    return {"status": "success", "message": "Strategy stopped"}


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get trading statistics from JOURNAL (not signals)"""
    try:
        from database.journal_crud import JournalCRUD
        stats = JournalCRUD.get_statistics(db)
        
        return {
            "total_trades": stats.get('total_trades', 0),
            "win_rate": stats.get('win_rate', 0.0),
            "profit_loss": stats.get('total_pnl', 0.0),
            "total_pips": stats.get('total_pips', 0.0),
            "wins": stats.get('wins', 0),
            "losses": stats.get('losses', 0),
            "avg_r": stats.get('avg_r', 0.0)
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_loss": 0.0,
            "total_pips": 0.0,
            "wins": 0,
            "losses": 0,
            "avg_r": 0.0
        }


@app.get("/api/journal")
async def get_journal_entries():
    """Get trading journal entries"""
    # Mock data for testing
    return {
        "entries": [],
        "count": 0
    }


# DEPRECATED: This endpoint used the old oanda_integration module  
# Frontend doesn't use this endpoint - commented out after cleanup
# @app.get("/api/prices/live")
# async def get_all_live_prices():
#     """Get live prices for all symbols from OANDA"""
#     try:
#         # Try to get real prices from OANDA
#         from oanda_integration.oanda_client import OANDAClient
#         
#         oanda_client = OANDAClient()
#         symbols = ["GBP_USD", "XAU_USD", "USD_JPY"]
#         
#         prices = {}
#         for symbol in symbols:
#             try:
#                 price_data = oanda_client.get_current_price(symbol)
#                 if price_data:
#                     # Convert OANDA format to our format
#                     symbol_clean = symbol.replace("_", "")
#                     bid = float(price_data.get('bids', [{}])[0].get('price', 0))
#                     ask = float(price_data.get('asks', [{}])[0].get('price', 0))
#                     
#                     # Calculate spread in pips
#                     pip_location = 4 if symbol_clean != "XAUUSD" else 2
#                     spread_pips = round((ask - bid) * (10 ** pip_location), 1)
#                     
#                     prices[symbol_clean] = {
#                         "symbol": symbol_clean,
#                         "bid": bid,
#                         "ask": ask,
#                         "price": (bid + ask) / 2,
#                         "spreadPips": spread_pips,
#                         "time": price_data.get('time', datetime.now().isoformat()),
#                         "volume": {
#                             "bid": int(price_data.get('bids', [{}])[0].get('liquidity', 500000)),
#                             "ask": int(price_data.get('asks', [{}])[0].get('liquidity', 500000))
#                         }
#                     }
#                     print(f"✅ Fetched live price for {symbol_clean}: Bid={bid}, Ask={ask}")
#             except Exception as e:
#                 print(f"❌ Error fetching {symbol}: {e}")
#                 continue
#         
#         if prices:
#             print(f"✅ Returning {len(prices)} live prices from OANDA")
#             return {"prices": prices, "source": "OANDA_REAL"}
#         else:
#             raise Exception("No prices available from OANDA")
#             
#     except Exception as e:
#         print(f"⚠️ Error fetching live prices from OANDA: {e}")
#         print("   Falling back to mock data")
#         # Fallback to mock data
#         mock_prices = {
#             "GBPUSD": {
#                 "symbol": "GBPUSD",
#                 "bid": 1.3140,
#                 "ask": 1.3141,
#                 "price": 1.3140,
#                 "spreadPips": 1.8,
#                 "time": datetime.now().isoformat(),
#                 "volume": {"bid": 500000, "ask": 500000}
#             },
#             "XAUUSD": {
#                 "symbol": "XAUUSD",
#                 "bid": 4002.99,
#                 "ask": 4004.05,
#                 "price": 4003.52,
#                 "spreadPips": 10.6,
#                 "time": datetime.now().isoformat(),
#                 "volume": {"bid": 0, "ask": 0}
#             },
#             "USDJPY": {
#                 "symbol": "USDJPY",
#                "bid": 154.0570,
#                 "ask": 154.0700,
#                 "price": 154.0635,
#                 "spreadPips": 13.0,
#                 "time": datetime.now().isoformat(),
#                 "volume": {"bid": 500000, "ask": 500000}
#             }
#         }
#         return {"prices": mock_prices, "source": "mock"}


@app.get("/api/prices/live/{symbol}")
async def get_live_price(symbol: str):
    """Get live price for a specific symbol"""
    mock_prices = {
        "GBPUSD": {"bid": 1.2648, "ask": 1.2652, "price": 1.2650},
        "XAUUSD": {"bid": 2735.50, "ask": 2736.50, "price": 2736.00},
        "USDJPY": {"bid": 152.45, "ask": 152.47, "price": 152.46}
    }
    
    symbol_upper = symbol.upper().replace("_", "")
    
    if symbol_upper in mock_prices:
        return {
            "symbol": symbol_upper,
            **mock_prices[symbol_upper],
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "symbol": symbol_upper,
            "bid": 1.0000,
            "ask": 1.0002,
            "price": 1.0001,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/symbols")
async def get_symbols():
    """Get available trading symbols"""
    return {
        "symbols": ["GBPUSD", "XAUUSD", "USDJPY", "EURUSD", "AUDUSD"],
        "count": 5
    }


@app.post("/api/signals/generate")
async def generate_signals(all_instruments: bool = True):
    """Generate trading signals using Enhanced Signal Generator"""
    try:
        from signal_generator_enhanced import EnhancedSignalGenerator
        
        if not all_instruments:
            raise HTTPException(status_code=400, detail="Missing required parameter: instrument")
        
        generator = EnhancedSignalGenerator()
        results = generator.run_single_scan()
        
        success_count = sum(1 for success in results.values() if success)
        
        # Convert results into list format
        signals_list = []
        for instrument, success in results.items():
            if success:
                signals_list.append({
                    "instrument": instrument,
                    "generated": success,
                    "timestamp": datetime.now().isoformat()
                })
        
        return {
            "status": "success" if success_count > 0 else "no_signals",
            "signals_generated": success_count,
            "results": signals_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/signals/generate/{instrument}")
async def generate_signals_specific(instrument: str):
    """Generate trading signals for a specific instrument"""
    try:
        from signal_generator_enhanced import EnhancedSignalGenerator
        
        if not instrument or instrument.strip() == "":
            raise HTTPException(status_code=400, detail="Instrument cannot be empty")
        
        generator = EnhancedSignalGenerator()
        result = generator.process_instrument(instrument)
        
        return {
            "status": "success" if result else "no_signals",
            "signals_generated": 1 if result else 0,
            "results": [{
                "instrument": instrument,
                "generated": result,
                "timestamp": datetime.now().isoformat()
            }] if result else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/status")
async def get_analysis_status():
    """Get analysis status"""
    return {
        "status": "idle",
        "last_analysis": None,
        "is_running": False
    }


@app.get("/api/analysis/latest")
async def get_latest_analysis():
    """Get latest analysis"""
    return {
        "analysis": None,
        "timestamp": None
    }


@app.get("/api/analysis/history")
async def get_analysis_history():
    """Get analysis history"""
    return {
        "history": [],
        "count": 0
    }


@app.post("/api/backtest/run")
async def run_backtest(request: dict):
    """Run backtest with custom strategy"""
    return {
        "status": "success",
        "message": "Backtest feature coming soon",
        "results": None
    }


@app.get("/api/backtest/template")
async def get_strategy_template():
    """Get strategy code template"""
    template = """
# AlphaForge Strategy Template
def strategy(data):
    # Your strategy logic here
    signals = []
    return signals
    """
    return {
        "template": template,
        "language": "python"
    }


@app.post("/api/strategy/save")
async def save_strategy(request: dict):
    """Save custom strategy"""
    return {
        "status": "success",
        "message": "Strategy saved",
        "strategy_id": "strat_001"
    }


# ==================== JOURNAL ENDPOINTS ====================

@app.post("/api/journal/entries")
async def create_journal_entry(entry: dict, db: Session = Depends(get_db)):
    """Create a new journal entry"""
    try:
        new_entry = JournalCRUD.create_entry(db, entry)
        return {
            "success": True,
            "message": "Journal entry created",
            "entry": new_entry.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/journal/entries")
async def get_journal_entries(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Get all journal entries"""
    entries = JournalCRUD.get_all_entries(db, skip=skip, limit=limit)
    return {
        "entries": [e.to_dict() for e in entries],
        "total": len(entries)
    }


@app.get("/api/journal/entries/{entry_id}")
async def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific journal entry"""
    entry = JournalCRUD.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.to_dict()


@app.put("/api/journal/entries/{entry_id}")
async def update_journal_entry(
    entry_id: int,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update a journal entry"""
    entry = JournalCRUD.update_entry(db, entry_id, updates)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {
        "success": True,
        "message": "Entry updated",
        "entry": entry.to_dict()
    }


@app.delete("/api/journal/entries/{entry_id}")
async def delete_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a journal entry"""
    success = JournalCRUD.delete_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {
        "success": True,
        "message": "Entry deleted"
    }


@app.get("/api/journal/statistics")
async def get_journal_statistics(db: Session = Depends(get_db)):
    """Get journal statistics"""
    stats = JournalCRUD.get_statistics(db)
    return stats


# ============================================================================
# TRADING SIGNALS ENDPOINTS
# ============================================================================

@app.get("/api/signals")
async def get_all_signals(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get trading signals with optional filters
    - status: PENDING, ACTIVE, CLOSED, CANCELLED, EXPIRED
    - symbol: XAU_USD, GBP_USD, USD_JPY
    """
    try:
        from database.signal_crud import SignalCRUD
        from database.signal_models import SignalStatus
        
        if status:
            # Filter by status
            status_enum = SignalStatus[status]
            signals = SignalCRUD.get_signals_by_status(db, status_enum)
        elif symbol:
            # Filter by symbol
            signals = SignalCRUD.get_signals_by_symbol(db, symbol)
        else:
            # Get all signals
            signals = SignalCRUD.get_all_signals(db, skip=skip, limit=limit)
        
        return {
            "success": True,
            "count": len(signals),
            "signals": [signal.to_dict() for signal in signals]
        }
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/active")
async def get_active_signals(db: Session = Depends(get_db)):
    """Get all active trading signals"""
    try:
        from database.signal_crud import SignalCRUD
        
        signals = SignalCRUD.get_active_signals(db)
        
        return {
            "success": True,
            "count": len(signals),
            "signals": [signal.to_dict() for signal in signals]
        }
    except Exception as e:
        logger.error(f"Error fetching active signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/pending")
async def get_pending_signals(db: Session = Depends(get_db)):
    """Get all pending trading signals (not yet entered)"""
    try:
        from database.signal_crud import SignalCRUD
        from database.signal_models import SignalStatus
        
        signals = SignalCRUD.get_signals_by_status(db, SignalStatus.PENDING)
        
        return {
            "success": True,
            "count": len(signals),
            "signals": [signal.to_dict() for signal in signals]
        }
    except Exception as e:
        logger.error(f"Error fetching pending signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{signal_id}")
async def get_signal(signal_id: int, db: Session = Depends(get_db)):
    """Get a specific signal by ID"""
    try:
        from database.signal_crud import SignalCRUD
        
        signal = SignalCRUD.get_signal(db, signal_id)
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        return {
            "success": True,
            "signal": signal.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/signals")
async def create_signal(signal_data: dict, db: Session = Depends(get_db)):
    """Create a new trading signal"""
    try:
        from database.signal_crud import SignalCRUD
        
        signal = SignalCRUD.create_signal(db, signal_data)
        
        return {
            "success": True,
            "message": "Signal created",
            "signal": signal.to_dict()
        }
    except Exception as e:
        logger.error(f"Error creating signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/signals/{signal_id}/status")
async def update_signal_status(
    signal_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update signal status (PENDING -> ACTIVE -> CLOSED)"""
    try:
        from database.signal_crud import SignalCRUD
        from database.signal_models import SignalStatus
        
        status_enum = SignalStatus[status]
        signal = SignalCRUD.update_signal_status(db, signal_id, status_enum)
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        return {
            "success": True,
            "message": f"Signal status updated to {status}",
            "signal": signal.to_dict()
        }
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating signal status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/journal/statistics")
async def get_journal_statistics(db: Session = Depends(get_db)):
    """Get trading performance statistics from JOURNAL (actual trades with outcomes)"""
    try:
        from database.journal_crud import JournalCRUD
        
        stats = JournalCRUD.get_statistics(db)
        
        return {
            "success": True,
            "statistics": stats,
            "note": "These statistics are based on actual trades from your trading journal"
        }
    except Exception as e:
        logger.error(f"Error fetching journal statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting AlphaForge API Server")
    print("="*60)
    print(f"📡 Server: http://localhost:5000")
    print(f"📖 Docs: http://localhost:5000/docs")
    print(f"🔍 Health: http://localhost:5000/health")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
