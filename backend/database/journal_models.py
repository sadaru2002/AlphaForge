"""
Trading Journal Database Models
Stores manual trade entries with full details including screenshots
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum
from datetime import datetime
from .signal_models import Base
import enum


class TradeType(enum.Enum):
    """Trade direction"""
    BUY = "BUY"
    SELL = "SELL"


class TradeOutcomeJournal(enum.Enum):
    """Trade outcome"""
    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"


class SessionType(enum.Enum):
    """Trading session"""
    LONDON = "LONDON"
    NEW_YORK = "NEW_YORK"
    ASIAN = "ASIAN"
    OVERLAP = "OVERLAP"


class JournalEntry(Base):
    """Manual trade journal entry"""
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trade Details
    open_time = Column(DateTime, nullable=False, index=True)
    close_time = Column(DateTime)
    symbol = Column(String(20), nullable=False, index=True)
    trade_type = Column(SQLEnum(TradeType), nullable=False)
    lots = Column(Float, nullable=False)
    
    # Prices
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # Performance
    pips = Column(Float)
    profit_loss = Column(Float)
    mae = Column(Float)  # Maximum Adverse Excursion
    mfe = Column(Float)  # Maximum Favorable Excursion
    r_value = Column(Float)  # Risk/Reward multiple
    
    # Trade Context
    trade_setup = Column(String(100))
    session = Column(SQLEnum(SessionType))
    duration_minutes = Column(Integer)
    
    # Notes and Analysis
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Screenshots (stored as file paths or base64)
    screenshot_entry = Column(Text)  # Entry screenshot
    screenshot_exit = Column(Text)   # Exit screenshot
    screenshot_analysis = Column(Text)  # Chart analysis screenshot
    
    # Outcome
    outcome = Column(SQLEnum(TradeOutcomeJournal))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'openTime': self.open_time.strftime('%Y-%m-%d %H:%M') if self.open_time else None,
            'closeTime': self.close_time.strftime('%Y-%m-%d %H:%M') if self.close_time else None,
            'symbol': self.symbol,
            'type': self.trade_type.value if self.trade_type else None,
            'lots': self.lots,
            'entry': self.entry_price,
            'exit': self.exit_price,
            'sl': self.stop_loss,
            'tp': self.take_profit,
            'pips': self.pips,
            'pl': self.profit_loss,
            'mae': self.mae,
            'mfe': self.mfe,
            'r': self.r_value,
            'setup': self.trade_setup,
            'session': self.session.value if self.session else None,
            'duration': f"{self.duration_minutes} min" if self.duration_minutes else None,
            'notes': self.notes,
            'tags': self.tags,
            'screenshot_entry': self.screenshot_entry,
            'screenshot_exit': self.screenshot_exit,
            'screenshot_analysis': self.screenshot_analysis,
            'outcome': self.outcome.value if self.outcome else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
