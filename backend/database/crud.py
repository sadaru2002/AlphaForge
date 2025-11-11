from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from .models import Signal, MarketData, PatternDetected, DailyPerformance, SystemLog
from .database import DATABASE_AVAILABLE
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def check_db_available(func):
    """Decorator to check if database is available"""
    def wrapper(*args, **kwargs):
        if not DATABASE_AVAILABLE:
            logger.debug(f"Database not available, skipping {func.__name__}")
            return None
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            return None
    return wrapper

class SignalCRUD:
    @staticmethod
    def create_signal(db: Session, signal_data: Dict[str, Any]) -> Signal:
        """Create a new signal"""
        signal = Signal(**signal_data)
        db.add(signal)
        db.commit()
        db.refresh(signal)
        logger.info(f"Created signal {signal.id} for {signal.symbol}")
        return signal
    
    @staticmethod
    def get_signals(db: Session, limit: int = 100, symbol: Optional[str] = None) -> List[Signal]:
        """Get recent signals"""
        query = db.query(Signal)
        if symbol:
            query = query.filter(Signal.symbol == symbol)
        return query.order_by(desc(Signal.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_signals_today(db: Session) -> List[Signal]:
        """Get today's signals"""
        today = date.today()
        return db.query(Signal).filter(
            func.date(Signal.timestamp) == today
        ).order_by(desc(Signal.timestamp)).all()
    
    @staticmethod
    def update_signal_outcome(db: Session, signal_id: int, outcome: str, 
                            actual_pnl: float = None, close_price: float = None) -> bool:
        """Update signal outcome"""
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            return False
        
        signal.outcome = outcome
        if actual_pnl is not None:
            signal.actual_pnl = actual_pnl
        if close_price is not None:
            signal.close_price = close_price
        signal.close_time = datetime.utcnow()
        
        db.commit()
        logger.info(f"Updated signal {signal_id} outcome to {outcome}")
        return True

class MarketDataCRUD:
    @staticmethod
    def store_market_data(db: Session, symbol: str, timeframe: str, 
                         data: List[Dict]) -> bool:
        """Store market data"""
        try:
            for row in data:
                market_data = MarketData(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=row['time'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row.get('tick_volume', 0)
                )
                db.merge(market_data)  # Use merge to handle duplicates
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_latest_data(db: Session, symbol: str, timeframe: str, 
                       limit: int = 500) -> List[MarketData]:
        """Get latest market data"""
        return db.query(MarketData).filter(
            MarketData.symbol == symbol,
            MarketData.timeframe == timeframe
        ).order_by(desc(MarketData.timestamp)).limit(limit).all()

class PatternCRUD:
    @staticmethod
    def store_pattern(db: Session, pattern_data: Dict[str, Any]) -> PatternDetected:
        """Store detected pattern"""
        pattern = PatternDetected(**pattern_data)
        db.add(pattern)
        db.commit()
        db.refresh(pattern)
        return pattern

class PerformanceCRUD:
    @staticmethod
    def get_daily_pnl(db: Session, target_date: date) -> Optional[Dict]:
        """Get daily P&L for a specific date"""
        performance = db.query(DailyPerformance).filter(
            DailyPerformance.date == target_date
        ).first()
        
        if performance:
            return {
                'total_signals': performance.total_signals,
                'signals_traded': performance.signals_traded,
                'wins': performance.wins,
                'losses': performance.losses,
                'win_rate': performance.win_rate,
                'total_pnl': performance.total_pnl,
                'max_drawdown': performance.max_drawdown
            }
        return None
    
    @staticmethod
    def update_daily_performance(db: Session, target_date: date, 
                                performance_data: Dict[str, Any]) -> bool:
        """Update daily performance"""
        performance = db.query(DailyPerformance).filter(
            DailyPerformance.date == target_date
        ).first()
        
        if not performance:
            performance = DailyPerformance(date=target_date)
            db.add(performance)
        
        for key, value in performance_data.items():
            setattr(performance, key, value)
        
        db.commit()
        return True

class LogCRUD:
    @staticmethod
    def log_event(db: Session, level: str, component: str, 
                 message: str, data: Dict = None) -> None:
        """Log system event"""
        log_entry = SystemLog(
            level=level,
            component=component,
            message=message,
            data=data
        )
        db.add(log_entry)
        db.commit()

# Alias for backward compatibility
SystemLogCRUD = LogCRUD

# Convenience functions
def create_signal(db: Session, **kwargs) -> Signal:
    return SignalCRUD.create_signal(db, kwargs)

def get_today_signals(db: Session) -> List[Signal]:
    return SignalCRUD.get_signals_today(db)

def get_daily_pnl(db: Session, target_date: date = None) -> Optional[Dict]:
    if target_date is None:
        target_date = date.today()
    return PerformanceCRUD.get_daily_pnl(db, target_date)

def log_info(db: Session, component: str, message: str, data: Dict = None):
    LogCRUD.log_event(db, "INFO", component, message, data)

def log_warning(db: Session, component: str, message: str, data: Dict = None):
    LogCRUD.log_event(db, "WARNING", component, message, data)

def log_error(db: Session, component: str, message: str, data: Dict = None):
    LogCRUD.log_event(db, "ERROR", component, message, data)

def get_signals(db: Session, limit: int = 100, symbol: str = None) -> List[Signal]:
    """Get recent signals - convenience function"""
    return SignalCRUD.get_signals(db, limit, symbol)