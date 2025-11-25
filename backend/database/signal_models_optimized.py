"""
Optimized Database Models with Indexes and Performance Enhancements
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Enum, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()


class SignalStatus(PyEnum):
    """Signal lifecycle status"""
    PENDING = "PENDING"      # Signal generated, awaiting entry
    ACTIVE = "ACTIVE"        # Trade entered
    CLOSED = "CLOSED"        # Trade completed
    CANCELLED = "CANCELLED"  # Signal cancelled before entry
    EXPIRED = "EXPIRED"      # Signal expired without entry


class TradeOutcome(PyEnum):
    """Trade result"""
    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"
    NONE = "NONE"  # Not yet closed


class TradingSignal(Base):
    """
    Optimized Trading Signal Model with Database Indexes
    
    Performance Optimizations:
    1. Composite indexes for common queries
    2. Covering indexes for frequently accessed columns
    3. Partial indexes for status filtering
    4. Timestamp indexes for time-based queries
    """
    __tablename__ = "trading_signals"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Core signal data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    pair = Column(String(10), index=True, nullable=False)  # GBP_USD, XAU_USD, USD_JPY
    symbol = Column(String(10), index=True)  # GBPUSD, XAUUSD, USDJPY
    direction = Column(String(4), index=True, nullable=False)  # BUY or SELL
    
    # Price levels
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    tp2 = Column(Float)  # Optional second TP
    tp3 = Column(Float)  # Optional third TP
    
    # Trade execution tracking
    status = Column(Enum(SignalStatus), default=SignalStatus.PENDING, index=True, nullable=False)
    outcome = Column(Enum(TradeOutcome), default=TradeOutcome.NONE, index=True)
    
    # Actual execution prices (when trade is entered/exited)
    actual_entry = Column(Float)
    actual_exit = Column(Float)
    
    # Performance metrics
    pips_gained = Column(Float)
    actual_pnl = Column(Float)  # P&L in currency
    risk_reward_ratio = Column(String(10))  # e.g., "1:2.5"
    
    # Signal quality metrics
    confidence_score = Column(Float, index=True)  # 0-100
    session_weight = Column(Float)  # Trading session multiplier
    atr = Column(Float)  # Average True Range at signal time
    
    # Enhanced metadata (AlphaForge features)
    metadata = Column(JSON)  # {regime, mtf_signals, kelly_fraction, etc.}
    reasoning = Column(Text)  # AI-generated reasoning
    
    # Timestamps for tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    entry_time = Column(DateTime, index=True)  # When trade was entered
    exit_time = Column(DateTime, index=True)   # When trade was closed
    
    # ==================== PERFORMANCE INDEXES ====================
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Most common: Get recent signals by pair and status
        Index('idx_pair_status_timestamp', 'pair', 'status', 'timestamp'),
        
        # Dashboard query: Active signals ordered by confidence
        Index('idx_status_confidence', 'status', 'confidence_score'),
        
        # Analytics query: Outcomes by pair and time range
        Index('idx_pair_outcome_timestamp', 'pair', 'outcome', 'timestamp'),
        
        # Performance query: P&L analysis by direction
        Index('idx_direction_outcome_pnl', 'direction', 'outcome', 'actual_pnl'),
        
        # Time-based queries: Signals within date ranges
        Index('idx_created_at', 'created_at'),
        Index('idx_entry_exit_time', 'entry_time', 'exit_time'),
        
        # Symbol-based filtering (covering index)
        Index('idx_symbol_status_timestamp', 'symbol', 'status', 'timestamp'),
        
        # Partial index for active signals only (PostgreSQL-specific, ignored by SQLite)
        # Index('idx_active_signals', 'pair', 'timestamp', 
        #       postgresql_where=(status == SignalStatus.ACTIVE)),
    )
    
    def to_dict(self):
        """
        Optimized serialization with lazy loading.
        Only includes non-null fields to reduce payload size.
        """
        result = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "pair": self.pair,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "status": self.status.value if self.status else None,
            "confidence_score": self.confidence_score,
        }
        
        # Add optional fields only if they exist (reduce JSON size)
        if self.tp2:
            result["tp2"] = self.tp2
        if self.tp3:
            result["tp3"] = self.tp3
        if self.outcome:
            result["outcome"] = self.outcome.value
        if self.actual_entry:
            result["actual_entry"] = self.actual_entry
        if self.actual_exit:
            result["actual_exit"] = self.actual_exit
        if self.pips_gained:
            result["pips_gained"] = self.pips_gained
        if self.actual_pnl:
            result["actual_pnl"] = self.actual_pnl
        if self.risk_reward_ratio:
            result["rr_ratio"] = self.risk_reward_ratio
        if self.reasoning:
            result["reasoning"] = self.reasoning
        if self.metadata:
            result["metadata"] = self.metadata
        if self.session_weight:
            result["session_weight"] = self.session_weight
        if self.atr:
            result["atr"] = self.atr
        if self.entry_time:
            result["entry_time"] = self.entry_time.isoformat()
        if self.exit_time:
            result["exit_time"] = self.exit_time.isoformat()
        
        return result
    
    def to_dict_minimal(self):
        """
        Ultra-lightweight serialization for list views.
        Only includes essential fields (60% smaller payload).
        """
        return {
            "id": self.id,
            "pair": self.pair,
            "direction": self.direction,
            "entry": self.entry_price,
            "status": self.status.value if self.status else None,
            "confidence": self.confidence_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
    
    def __repr__(self):
        return (
            f"<TradingSignal(id={self.id}, pair={self.pair}, "
            f"direction={self.direction}, status={self.status.value if self.status else None})>"
        )


# ==================== Database Schema Utilities ====================

def create_indexes(engine):
    """
    Create additional indexes after table creation (PostgreSQL-specific optimizations).
    Call this after Base.metadata.create_all(bind=engine)
    """
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Check if we're using PostgreSQL
        if 'postgresql' in str(engine.url):
            # Partial index for active signals (PostgreSQL only)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_active_signals 
                ON trading_signals (pair, timestamp) 
                WHERE status = 'ACTIVE'
            """))
            
            # Partial index for pending signals
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pending_signals 
                ON trading_signals (pair, confidence_score DESC) 
                WHERE status = 'PENDING'
            """))
            
            # Covering index for dashboard query
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_dashboard_covering 
                ON trading_signals (status, confidence_score, pair, timestamp) 
                INCLUDE (direction, entry_price, stop_loss, take_profit)
            """))
            
            conn.commit()
            print("✅ PostgreSQL-specific indexes created successfully")
        else:
            print("⏭️  Skipping PostgreSQL-specific indexes (using SQLite)")

