"""
Optimized Database Queries for Trading Signals
Implements eager loading, batch operations, and query optimization
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_, case, text
from .signal_models import TradingSignal, TradeAnalytics, SignalStatus, TradeOutcome


class OptimizedSignalQueries:
    """Optimized database queries with indexing and eager loading"""
    
    @staticmethod
    def get_signals_optimized(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[TradingSignal], int]:
        """
        Optimized query with filters and pagination
        Returns (signals, total_count)
        """
        # Build query with filters
        query = db.query(TradingSignal)
        
        # Apply filters
        if status:
            query = query.filter(TradingSignal.status == status)
        
        if symbol:
            query = query.filter(TradingSignal.symbol == symbol)
        
        if start_date:
            query = query.filter(TradingSignal.timestamp >= start_date)
        
        if end_date:
            query = query.filter(TradingSignal.timestamp <= end_date)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply ordering and pagination
        signals = (
            query
            .order_by(TradingSignal.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return signals, total_count
    
    @staticmethod
    def get_statistics_optimized(db: Session) -> Dict:
        """
        Optimized statistics query using SQL aggregation
        Single query instead of multiple
        """
        result = db.query(
            func.count(TradingSignal.id).label('total_trades'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.WIN, 1), else_=0)).label('winning_trades'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.LOSS, 1), else_=0)).label('losing_trades'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.WIN, TradingSignal.actual_pnl), else_=0)).label('total_profit'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.LOSS, TradingSignal.actual_pnl), else_=0)).label('total_loss'),
            func.sum(TradingSignal.actual_pnl).label('net_pnl'),
            func.avg(TradingSignal.actual_pnl).label('avg_pnl'),
            func.max(TradingSignal.actual_pnl).label('max_win'),
            func.min(TradingSignal.actual_pnl).label('max_loss'),
            func.avg(TradingSignal.pips_gained).label('avg_pips'),
            func.avg(TradingSignal.duration_hours).label('avg_duration'),
        ).filter(
            TradingSignal.status == SignalStatus.CLOSED
        ).first()
        
        if not result or result.total_trades == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'total_loss': 0.0,
                'net_pnl': 0.0,
                'avg_pnl': 0.0,
                'max_win': 0.0,
                'max_loss': 0.0,
                'avg_pips': 0.0,
                'avg_duration': 0.0,
                'profit_factor': 0.0,
                'expectancy': 0.0,
            }
        
        # Calculate derived metrics
        win_rate = (result.winning_trades / result.total_trades * 100) if result.total_trades > 0 else 0
        profit_factor = abs(result.total_profit / result.total_loss) if result.total_loss != 0 else float('inf')
        expectancy = result.avg_pnl or 0
        
        return {
            'total_trades': result.total_trades or 0,
            'winning_trades': result.winning_trades or 0,
            'losing_trades': result.losing_trades or 0,
            'win_rate': round(win_rate, 2),
            'total_profit': float(result.total_profit or 0),
            'total_loss': float(result.total_loss or 0),
            'net_pnl': float(result.net_pnl or 0),
            'avg_pnl': float(result.avg_pnl or 0),
            'max_win': float(result.max_win or 0),
            'max_loss': float(result.max_loss or 0),
            'avg_pips': float(result.avg_pips or 0),
            'avg_duration': float(result.avg_duration or 0),
            'profit_factor': float(profit_factor) if profit_factor != float('inf') else 999.99,
            'expectancy': float(expectancy),
        }
    
    @staticmethod
    def get_symbol_performance_optimized(db: Session, symbol: str) -> Dict:
        """
        Optimized symbol-specific performance query
        """
        result = db.query(
            func.count(TradingSignal.id).label('total_trades'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.WIN, 1), else_=0)).label('wins'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.LOSS, 1), else_=0)).label('losses'),
            func.sum(TradingSignal.actual_pnl).label('total_pnl'),
            func.avg(TradingSignal.actual_pnl).label('avg_pnl'),
            func.sum(TradingSignal.pips_gained).label('total_pips'),
        ).filter(
            and_(
                TradingSignal.symbol == symbol,
                TradingSignal.status == SignalStatus.CLOSED
            )
        ).first()
        
        if not result or result.total_trades == 0:
            return {
                'symbol': symbol,
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0,
                'total_pips': 0.0,
            }
        
        return {
            'symbol': symbol,
            'total_trades': result.total_trades,
            'wins': result.wins or 0,
            'losses': result.losses or 0,
            'win_rate': round((result.wins / result.total_trades * 100) if result.total_trades > 0 else 0, 2),
            'total_pnl': float(result.total_pnl or 0),
            'avg_pnl': float(result.avg_pnl or 0),
            'total_pips': float(result.total_pips or 0),
        }
    
    @staticmethod
    def get_daily_analytics_optimized(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get daily aggregated analytics
        Optimized with date grouping
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Use SQL date function for grouping
        results = db.query(
            func.date(TradingSignal.timestamp).label('date'),
            func.count(TradingSignal.id).label('trades'),
            func.sum(case((TradingSignal.outcome == TradeOutcome.WIN, 1), else_=0)).label('wins'),
            func.sum(TradingSignal.actual_pnl).label('pnl'),
        ).filter(
            and_(
                TradingSignal.timestamp >= start_date,
                TradingSignal.timestamp <= end_date,
                TradingSignal.status == SignalStatus.CLOSED
            )
        ).group_by(
            func.date(TradingSignal.timestamp)
        ).order_by(
            func.date(TradingSignal.timestamp)
        ).all()
        
        return [
            {
                'date': str(r.date),
                'trades': r.trades,
                'wins': r.wins or 0,
                'pnl': float(r.pnl or 0),
                'win_rate': round((r.wins / r.trades * 100) if r.trades > 0 else 0, 2),
            }
            for r in results
        ]
    
    @staticmethod
    def batch_update_signals(db: Session, updates: List[Tuple[int, Dict]]):
        """
        Batch update multiple signals efficiently
        Updates: [(signal_id, {field: value}), ...]
        """
        for signal_id, data in updates:
            db.query(TradingSignal).filter(
                TradingSignal.id == signal_id
            ).update(data)
        
        db.commit()
    
    @staticmethod
    def get_recent_signals_optimized(
        db: Session,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[TradingSignal]:
        """
        Get most recent signals with optimized query
        """
        query = db.query(TradingSignal)
        
        if status:
            query = query.filter(TradingSignal.status == status)
        
        return (
            query
            .order_by(TradingSignal.timestamp.desc())
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def create_database_indexes(db: Session):
        """
        Create performance indexes on critical columns
        Call this once during database initialization
        """
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_signal_status ON trading_signals(status)",
            "CREATE INDEX IF NOT EXISTS idx_signal_symbol ON trading_signals(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_signal_timestamp ON trading_signals(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_signal_outcome ON trading_signals(outcome)",
            "CREATE INDEX IF NOT EXISTS idx_signal_status_timestamp ON trading_signals(status, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_signal_symbol_status ON trading_signals(symbol, status)",
        ]
        
        for index_sql in indexes:
            try:
                db.execute(text(index_sql))
                db.commit()
            except Exception as e:
                print(f"Index creation warning: {e}")
                db.rollback()
