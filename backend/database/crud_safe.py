"""
Safe CRUD operations that work with or without database
"""
from typing import List, Optional, Dict, Any
from datetime import date
import logging

logger = logging.getLogger(__name__)

# Try to import database components
try:
    from .database import DATABASE_AVAILABLE, get_db
    from .crud import SignalCRUD, PerformanceCRUD, SystemLogCRUD
    DB_IMPORTED = True
except Exception as e:
    logger.warning(f"Database not available: {e}")
    DATABASE_AVAILABLE = False
    DB_IMPORTED = False

def create_signal(db, **signal_data):
    """Create a signal (safe - returns None if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        logger.debug("Database not available, signal not persisted")
        return None
    
    try:
        return SignalCRUD.create_signal(db, signal_data)
    except Exception as e:
        logger.error(f"Error creating signal: {e}")
        return None

def get_signals(db, limit: int = 100, symbol: Optional[str] = None):
    """Get signals (safe - returns empty list if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        return []
    
    try:
        return SignalCRUD.get_signals(db, limit, symbol)
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        return []

def get_today_signals(db):
    """Get today's signals (safe - returns empty list if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        return []
    
    try:
        return SignalCRUD.get_signals_today(db)
    except Exception as e:
        logger.error(f"Error getting today's signals: {e}")
        return []

def get_daily_pnl(db, target_date: date = None):
    """Get daily P&L (safe - returns None if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        return None
    
    try:
        return PerformanceCRUD.get_daily_pnl(db, target_date or date.today())
    except Exception as e:
        logger.error(f"Error getting daily P&L: {e}")
        return None

def log_info(db, component: str, message: str):
    """Log info (safe - does nothing if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        return
    
    try:
        SystemLogCRUD.log_info(db, component, message)
    except Exception as e:
        logger.debug(f"Error logging info: {e}")

def log_warning(db, component: str, message: str):
    """Log warning (safe - does nothing if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        return
    
    try:
        SystemLogCRUD.log_warning(db, component, message)
    except Exception as e:
        logger.debug(f"Error logging warning: {e}")

def log_error(db, component: str, message: str):
    """Log error (safe - does nothing if DB unavailable)"""
    if not DATABASE_AVAILABLE or not DB_IMPORTED:
        return
    
    try:
        SystemLogCRUD.log_error(db, component, message)
    except Exception as e:
        logger.debug(f"Error logging error: {e}")

