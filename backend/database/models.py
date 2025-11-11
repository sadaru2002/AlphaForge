from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Date, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    symbol = Column(String(10), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, NO_TRADE
    
    # Trade Details
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit_1 = Column(Float)
    take_profit_2 = Column(Float)
    risk_reward_1 = Column(Float)
    risk_reward_2 = Column(Float)
    position_size = Column(Float)
    
    # Analysis
    confidence_score = Column(Integer)
    setup_type = Column(String(100))
    strategy_used = Column(String(50))
    
    # Market Conditions
    daily_bias = Column(String(20))
    session = Column(String(50))
    market_structure = Column(String(20))
    
    # Gemini Analysis
    gemini_reasoning = Column(Text)
    confirmations = Column(JSON)
    risks = Column(JSON)
    
    # Outcome (if traded)
    was_traded = Column(Boolean, default=False)
    outcome = Column(String(20))  # WIN, LOSS, BREAKEVEN, RUNNING
    actual_pnl = Column(Float)
    close_price = Column(Float)
    close_time = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger)
    
    # Unique constraint
    __table_args__ = (
        {'extend_existing': True}
    )

class PatternDetected(Base):
    __tablename__ = "patterns_detected"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    symbol = Column(String(10), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    pattern_type = Column(String(50), nullable=False)
    pattern_data = Column(JSON)
    price_level = Column(Float)
    strength_score = Column(Integer)
    created_at = Column(DateTime, default=func.now())

class DailyPerformance(Base):
    __tablename__ = "daily_performance"
    
    date = Column(Date, primary_key=True)
    total_signals = Column(Integer, default=0)
    signals_traded = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float)
    total_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    best_pair = Column(String(10))
    best_strategy = Column(String(50))

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    component = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON)