"""
Database models for trading signals and trade tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class SignalStatus(enum.Enum):
    """Signal lifecycle status"""
    PENDING = "PENDING"       # Signal generated, not yet entered
    ACTIVE = "ACTIVE"         # Trade is active
    CLOSED = "CLOSED"         # Trade closed
    CANCELLED = "CANCELLED"   # Signal cancelled before entry
    EXPIRED = "EXPIRED"       # Signal expired without entry


class TradeOutcome(enum.Enum):
    """Trade result classification"""
    WIN = "WIN"               # Hit take profit
    LOSS = "LOSS"             # Hit stop loss
    BREAKEVEN = "BREAKEVEN"   # Closed at breakeven
    MANUAL_CLOSE = "MANUAL"   # Manually closed


class TradingSignal(Base):
    """
    Complete trading signal tracking with entry, exit, and outcome
    """
    __tablename__ = "trading_signals"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Signal Generation
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # BUY or SELL
    
    # Price Levels
    entry = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    tp1 = Column(Float, nullable=False)
    tp2 = Column(Float)
    tp3 = Column(Float)
    
    # Risk Management
    rr_ratio = Column(String(10))  # e.g., "1:2"
    position_size = Column(Float)  # Lot size or units
    risk_amount = Column(Float)    # Amount risked in dollars
    
    # Signal Quality
    confidence_score = Column(Float)  # 0-100
    signal_strength = Column(String(20))  # STRONG, MEDIUM, WEAK
    reasoning = Column(Text)  # AI analysis reasoning
    
    # Trade Execution
    status = Column(SQLEnum(SignalStatus), default=SignalStatus.PENDING, nullable=False, index=True)
    entry_time = Column(DateTime)  # When trade was entered
    entry_price = Column(Float)    # Actual entry price (may differ from signal)
    exit_time = Column(DateTime)   # When trade was closed
    exit_price = Column(Float)     # Actual exit price
    
    # Trade Outcome
    outcome = Column(SQLEnum(TradeOutcome), index=True)
    pips_captured = Column(Float)
    actual_pnl = Column(Float)     # Actual profit/loss in dollars
    potential_pnl = Column(Float)  # What could have been earned
    
    # Trade Metrics
    duration_hours = Column(Float)  # How long trade was open
    mae = Column(Float)  # Maximum Adverse Excursion
    mfe = Column(Float)  # Maximum Favorable Excursion
    slippage = Column(Float)  # Entry slippage in pips
    
    # Market Context
    market_condition = Column(String(50))  # TRENDING, RANGING, VOLATILE
    session = Column(String(20))  # LONDON, NEW_YORK, ASIAN, OVERLAP
    volatility_level = Column(Float)  # ATR or similar
    
    # Notes & Tags
    notes = Column(Text)
    tags = Column(String(200))  # Comma-separated tags
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<TradingSignal {self.id}: {self.symbol} {self.direction} @ {self.entry} - {self.status}>"
    
    def to_dict(self):
        """Convert signal to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'symbol': self.symbol,
            'direction': self.direction,
            'entry': self.entry,
            'stop_loss': self.stop_loss,
            'tp1': self.tp1,
            'tp2': self.tp2,
            'tp3': self.tp3,
            'rr_ratio': self.rr_ratio,
            'position_size': self.position_size,
            'risk_amount': self.risk_amount,
            'confidence_score': self.confidence_score,
            'signal_strength': self.signal_strength,
            'reasoning': self.reasoning,
            'status': self.status.value if self.status else None,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'entry_price': self.entry_price,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'exit_price': self.exit_price,
            'outcome': self.outcome.value if self.outcome else None,
            'pips_captured': self.pips_captured,
            'actual_pnl': self.actual_pnl,
            'potential_pnl': self.potential_pnl,
            'duration_hours': self.duration_hours,
            'mae': self.mae,
            'mfe': self.mfe,
            'slippage': self.slippage,
            'market_condition': self.market_condition,
            'session': self.session,
            'volatility_level': self.volatility_level,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TradeAnalytics(Base):
    """
    Aggregate analytics for trade performance tracking
    """
    __tablename__ = "trade_analytics"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Daily Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    breakeven_trades = Column(Integer, default=0)
    
    # Performance Metrics
    win_rate = Column(Float)  # Percentage
    profit_factor = Column(Float)
    total_pnl = Column(Float)
    gross_profit = Column(Float)
    gross_loss = Column(Float)
    
    # Risk Metrics
    avg_win = Column(Float)
    avg_loss = Column(Float)
    largest_win = Column(Float)
    largest_loss = Column(Float)
    expectancy = Column(Float)
    
    # Trade Quality
    avg_duration = Column(Float)  # Hours
    avg_rr_achieved = Column(Float)
    avg_confidence = Column(Float)
    
    # Symbol Performance
    best_symbol = Column(String(20))
    worst_symbol = Column(String(20))
    
    # Session Performance
    best_session = Column(String(20))
    worst_session = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'breakeven_trades': self.breakeven_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_pnl': self.total_pnl,
            'gross_profit': self.gross_profit,
            'gross_loss': self.gross_loss,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'expectancy': self.expectancy,
            'avg_duration': self.avg_duration,
            'avg_rr_achieved': self.avg_rr_achieved,
            'avg_confidence': self.avg_confidence,
            'best_symbol': self.best_symbol,
            'worst_symbol': self.worst_symbol,
            'best_session': self.best_session,
            'worst_session': self.worst_session,
        }
