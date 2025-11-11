"""
CRUD operations for Trading Journal
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from .journal_models import JournalEntry, TradeType, SessionType, TradeOutcomeJournal


class JournalCRUD:
    """Database operations for trading journal"""
    
    @staticmethod
    def create_entry(db: Session, entry_data: dict) -> JournalEntry:
        """Create a new journal entry"""
        # Convert datetime strings to datetime objects
        if 'open_time' in entry_data:
            if isinstance(entry_data['open_time'], str) and entry_data['open_time']:
                try:
                    entry_data['open_time'] = datetime.fromisoformat(entry_data['open_time'].replace('Z', '+00:00'))
                except:
                    try:
                        entry_data['open_time'] = datetime.strptime(entry_data['open_time'], '%Y-%m-%dT%H:%M')
                    except:
                        entry_data['open_time'] = None
            elif not entry_data['open_time']:
                entry_data['open_time'] = None
        
        if 'close_time' in entry_data:
            if isinstance(entry_data['close_time'], str) and entry_data['close_time']:
                try:
                    entry_data['close_time'] = datetime.fromisoformat(entry_data['close_time'].replace('Z', '+00:00'))
                except:
                    try:
                        entry_data['close_time'] = datetime.strptime(entry_data['close_time'], '%Y-%m-%dT%H:%M')
                    except:
                        entry_data['close_time'] = None
            elif not entry_data['close_time']:
                entry_data['close_time'] = None
        
        # Remove empty string values and convert them to None
        for key in list(entry_data.keys()):
            if entry_data[key] == '':
                entry_data[key] = None
        
        # Convert string enums to proper enum types
        if 'trade_type' in entry_data and isinstance(entry_data['trade_type'], str):
            entry_data['trade_type'] = TradeType[entry_data['trade_type']]
        
        if 'session' in entry_data and isinstance(entry_data['session'], str):
            entry_data['session'] = SessionType[entry_data['session']]
            
        if 'outcome' in entry_data and isinstance(entry_data['outcome'], str):
            entry_data['outcome'] = TradeOutcomeJournal[entry_data['outcome']]
        
        entry = JournalEntry(**entry_data)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_entry(db: Session, entry_id: int) -> Optional[JournalEntry]:
        """Get a single journal entry by ID"""
        return db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    
    @staticmethod
    def get_all_entries(db: Session, skip: int = 0, limit: int = 1000) -> List[JournalEntry]:
        """Get all journal entries with pagination"""
        return db.query(JournalEntry)\
            .order_by(JournalEntry.open_time.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_entries_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> List[JournalEntry]:
        """Get entries within date range"""
        return db.query(JournalEntry)\
            .filter(JournalEntry.open_time >= start_date)\
            .filter(JournalEntry.open_time <= end_date)\
            .order_by(JournalEntry.open_time.desc())\
            .all()
    
    @staticmethod
    def get_entries_by_symbol(db: Session, symbol: str) -> List[JournalEntry]:
        """Get entries for specific symbol"""
        return db.query(JournalEntry)\
            .filter(JournalEntry.symbol == symbol)\
            .order_by(JournalEntry.open_time.desc())\
            .all()
    
    @staticmethod
    def update_entry(db: Session, entry_id: int, updates: dict) -> Optional[JournalEntry]:
        """Update a journal entry"""
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            return None
        
        # Convert string enums if needed
        if 'trade_type' in updates and isinstance(updates['trade_type'], str):
            updates['trade_type'] = TradeType[updates['trade_type']]
        
        if 'session' in updates and isinstance(updates['session'], str):
            updates['session'] = SessionType[updates['session']]
            
        if 'outcome' in updates and isinstance(updates['outcome'], str):
            updates['outcome'] = TradeOutcomeJournal[updates['outcome']]
        
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.updated_at = datetime.now()
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def delete_entry(db: Session, entry_id: int) -> bool:
        """Delete a journal entry"""
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            return False
        
        db.delete(entry)
        db.commit()
        return True
    
    @staticmethod
    def get_statistics(db: Session) -> dict:
        """Get journal statistics"""
        entries = db.query(JournalEntry).all()
        
        if not entries:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_pips': 0,
                'avg_r': 0
            }
        
        total_trades = len(entries)
        wins = len([e for e in entries if e.outcome == TradeOutcomeJournal.WIN])
        losses = len([e for e in entries if e.outcome == TradeOutcomeJournal.LOSS])
        
        total_pnl = sum([e.profit_loss for e in entries if e.profit_loss])
        total_pips = sum([e.pips for e in entries if e.pips])
        r_values = [e.r_value for e in entries if e.r_value]
        avg_r = sum(r_values) / len(r_values) if r_values else 0
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round((wins / total_trades * 100) if total_trades > 0 else 0, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pips': round(total_pips, 2),
            'avg_r': round(avg_r, 2)
        }
