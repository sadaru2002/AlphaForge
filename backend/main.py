"""
FastAPI Main Application
Complete trading system backend with WebSocket support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import uvicorn

from .database.database import get_db, init_database
from .database.crud import get_signals, get_daily_pnl, log_info, log_error
from .signal_generator.generator import SignalGenerator
from .signal_generator.validator import SignalValidator
from .notifications.telegram import TelegramNotifier
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components (global)
signal_generator = None
signal_validator = None
telegram_notifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager (startup and shutdown)"""
    global signal_generator, signal_validator, telegram_notifier
    
    # Startup
    try:
        logger.info("Starting AlphaForge Trading System...")
        
        # Initialize database (skip if PostgreSQL not available)
        try:
            init_database()
            logger.info("Database initialized")
        except Exception as db_error:
            logger.warning(f"Database initialization failed: {db_error}")
            logger.info("Running in demo mode without database")
        
        # Initialize components
        signal_validator = SignalValidator(
            min_confidence=settings.MIN_CONFIDENCE,
            min_rr_ratio=settings.MIN_RR_RATIO,
            max_daily_signals=settings.MAX_SIGNALS_PER_DAY
        )
        
        telegram_notifier = TelegramNotifier(
            token=settings.TELEGRAM_TOKEN,
            chat_id=settings.TELEGRAM_CHAT_ID
        )
        
        # Initialize signal generator with database session
        db = next(get_db())
        signal_generator = SignalGenerator(db)
        
        logger.info("Trading system initialized successfully")
        
        # Start background tasks
        asyncio.create_task(background_signal_generation())
        asyncio.create_task(background_health_check())
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down AlphaForge Trading System...")
    if signal_generator and signal_generator.mt5:
        signal_generator.mt5.disconnect()
    logger.info("Shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Gemini Pro Trading System",
    description="Multi-strategy AI-powered trading system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
# Allow multiple frontend origins for development and production
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    settings.FRONTEND_URL,
    settings.FRONTEND_URL_PRODUCTION,
    "https://alpha-forge.vercel.app",  # Vercel deployment
    "https://*.vercel.app",  # Any Vercel subdomain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for connection testing
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Routes
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Gemini Pro Trading System",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = next(get_db())
        
        # Check MT5 connection
        mt5_status = "connected" if signal_generator and signal_generator.mt5.connected else "disconnected"
        
        # Check Gemini connection
        gemini_status = "connected" if signal_generator and signal_generator.gemini_client.test_connection() else "disconnected"
        
        return {
            "status": "healthy",
            "database": "connected",
            "mt5": mt5_status,
            "gemini": gemini_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.get("/signals")
async def get_signals_endpoint(limit: int = 50, symbol: str = None, db: Session = Depends(get_db)):
    """Get recent signals"""
    try:
        signals = get_signals(db, limit=limit, symbol=symbol)
        return {
            "signals": [
                {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "entry_price": signal.entry_price,
                    "stop_loss": signal.stop_loss,
                    "take_profit_1": signal.take_profit_1,
                    "confidence_score": signal.confidence_score,
                    "timestamp": signal.timestamp.isoformat(),
                    "was_traded": signal.was_traded,
                    "outcome": signal.outcome
                }
                for signal in signals
            ],
            "count": len(signals)
        }
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/today")
async def get_today_signals(db: Session = Depends(get_db)):
    """Get today's signals"""
    try:
        signals = get_signals(db, limit=100)
        today_signals = [s for s in signals if s.timestamp.date() == datetime.now().date()]
        
        return {
            "signals": [
                {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "entry_price": signal.entry_price,
                    "confidence_score": signal.confidence_score,
                    "timestamp": signal.timestamp.isoformat()
                }
                for signal in today_signals
            ],
            "count": len(today_signals)
        }
    except Exception as e:
        logger.error(f"Error getting today's signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signals/generate")
async def generate_signals_endpoint(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Generate signals for all symbols"""
    try:
        if not signal_generator:
            raise HTTPException(status_code=500, detail="Signal generator not initialized")
        
        # Generate signals in background
        background_tasks.add_task(generate_signals_task, db)
        
        return {
            "message": "Signal generation started",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting signal generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/daily")
async def get_daily_performance(db: Session = Depends(get_db)):
    """Get daily performance statistics"""
    try:
        today = datetime.now().date()
        performance = get_daily_pnl(db, today)
        
        if not performance:
            return {
                "date": today.isoformat(),
                "total_signals": 0,
                "signals_traded": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "total_pnl": 0
            }
        
        return {
            "date": today.isoformat(),
            **performance
        }
    except Exception as e:
        logger.error(f"Error getting daily performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account/info")
async def get_account_info():
    """Get account information"""
    try:
        if not signal_generator or not signal_generator.mt5:
            raise HTTPException(status_code=500, detail="MT5 not connected")
        
        account_info = signal_generator.mt5.get_account_info()
        if not account_info:
            raise HTTPException(status_code=500, detail="Failed to get account info")
        
        return account_info
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "M15", bars: int = 100):
    """Get market data for a symbol"""
    try:
        if not signal_generator or not signal_generator.mt5:
            raise HTTPException(status_code=500, detail="MT5 not connected")
        
        data = signal_generator.mt5.get_market_data(symbol, timeframe, bars)
        if data is None:
            raise HTTPException(status_code=404, detail="No data available")
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "bars": len(data),
            "data": data.to_dict('records')
        }
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def generate_signals_task(db: Session):
    """Background task to generate signals"""
    try:
        logger.info("Starting background signal generation")
        
        if not signal_generator:
            logger.error("Signal generator not available")
            return
        
        # Generate signals for all symbols
        signals = await signal_generator.generate_all_signals()
        
        # Validate signals
        if signal_validator:
            daily_stats = get_daily_pnl(db)
            validation_results = signal_validator.validate_batch(signals, daily_stats)
            logger.info(f"Signal validation: {validation_results['valid_signals']}/{validation_results['total_signals']} valid")
        
        # Send notifications for valid signals
        valid_signals = [s for s in signals if s.get('setup_details', {}).get('direction') != 'NO_TRADE']
        if valid_signals and telegram_notifier:
            await telegram_notifier.send_signal_notifications(valid_signals)
        
        # Broadcast to WebSocket clients
        summary = signal_generator.get_signal_summary(signals)
        await manager.broadcast(json.dumps({
            "type": "signals_generated",
            "data": summary,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))
        
        logger.info(f"Background signal generation completed: {len(signals)} signals")
        
    except Exception as e:
        logger.error(f"Error in background signal generation: {e}")
        log_error(db, "BackgroundTask", f"Signal generation error: {str(e)}")

async def background_signal_generation():
    """Periodic signal generation"""
    while True:
        try:
            await asyncio.sleep(300)  # Generate signals every 5 minutes
            
            if signal_generator:
                db = next(get_db())
                await generate_signals_task(db)
                
        except Exception as e:
            logger.error(f"Error in periodic signal generation: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

async def background_health_check():
    """Periodic health check"""
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            
            # Check MT5 connection
            if signal_generator and signal_generator.mt5:
                if not signal_generator.mt5.connected:
                    logger.warning("MT5 disconnected, attempting to reconnect...")
                    signal_generator.mt5.connect()
            
            # Broadcast health status
            await manager.broadcast(json.dumps({
                "type": "health_check",
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            await asyncio.sleep(30)

# WebSocket test page
@app.get("/test")
async def test_websocket():
    """Test WebSocket connection"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <div id="messages"></div>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const message = document.createElement('div');
                message.textContent = event.data;
                messages.appendChild(message);
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ═══════════════════════════════════════════════════════════════════════
# OANDA LIVE PRICE ENDPOINTS (For Frontend Real-Time Updates)
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/prices/live")
async def get_live_prices():
    """Get current live prices from OANDA"""
    try:
        from .oanda_integration.oanda_client import OANDAClient, mt5_to_oanda
        
        oanda = OANDAClient(
            api_key=settings.OANDA_API_KEY,
            account_id=settings.OANDA_ACCOUNT_ID,
            base_url=settings.OANDA_BASE_URL
        )
        
        if not oanda.connect():
            raise HTTPException(status_code=500, detail="Cannot connect to OANDA")
        
        # Get prices for trading symbols
        symbols = [mt5_to_oanda(s) for s in settings.SYMBOLS.split(',')]
        prices = oanda.get_live_prices(symbols)
        
        return {
            "prices": prices,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching live prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prices/live/{symbol}")
async def get_live_price(symbol: str):
    """Get live price for a specific symbol"""
    try:
        from .oanda_integration.oanda_client import OANDAClient, mt5_to_oanda
        
        oanda = OANDAClient(
            api_key=settings.OANDA_API_KEY,
            account_id=settings.OANDA_ACCOUNT_ID,
            base_url=settings.OANDA_BASE_URL
        )
        
        if not oanda.connect():
            raise HTTPException(status_code=500, detail="Cannot connect to OANDA")
        
        # Convert MT5 symbol to OANDA format
        oanda_symbol = mt5_to_oanda(symbol)
        price = oanda.get_single_price(oanda_symbol)
        
        if not price:
            raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
        
        return {
            "symbol": symbol,
            "data": price,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account/summary")
async def get_account_summary():
    """Get OANDA account summary"""
    try:
        from .oanda_integration.oanda_client import OANDAClient
        
        oanda = OANDAClient(
            api_key=settings.OANDA_API_KEY,
            account_id=settings.OANDA_ACCOUNT_ID,
            base_url=settings.OANDA_BASE_URL
        )
        
        if not oanda.connect():
            raise HTTPException(status_code=500, detail="Cannot connect to OANDA")
        
        account = oanda.get_account_summary()
        if not account:
            raise HTTPException(status_code=500, detail="Failed to fetch account summary")
        
        return {
            "account": account['account'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for streaming live prices"""
    await websocket.accept()
    try:
        from .oanda_integration.oanda_client import OANDAClient, mt5_to_oanda
        import asyncio
        
        oanda = OANDAClient(
            api_key=settings.OANDA_API_KEY,
            account_id=settings.OANDA_ACCOUNT_ID,
            base_url=settings.OANDA_BASE_URL
        )
        
        while True:
            # Send live prices every 5 seconds
            await asyncio.sleep(5)
            
            symbols = [mt5_to_oanda(s) for s in settings.SYMBOLS.split(',')]
            prices = oanda.get_live_prices(symbols)
            
            if prices:
                await websocket.send_json({
                    "type": "price_update",
                    "data": prices,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
    except WebSocketDisconnect:
        logger.info("WebSocket prices disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

