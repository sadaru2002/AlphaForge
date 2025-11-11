"""
CRUD operations for trading signals database
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from .signal_models import TradingSignal, TradeAnalytics, SignalStatus, TradeOutcome


class SignalCRUD:
    """Database operations for trading signals"""
    
    @staticmethod
    def create_signal(db: Session, signal_data: dict) -> TradingSignal:
        """Create a new trading signal"""
        signal = TradingSignal(**signal_data)
        db.add(signal)
        db.commit()
        db.refresh(signal)
        return signal
    
    @staticmethod
    def get_signal(db: Session, signal_id: int) -> Optional[TradingSignal]:
        """Get a signal by ID"""
        return db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
    
    @staticmethod
    def get_all_signals(db: Session, skip: int = 0, limit: int = 100) -> List[TradingSignal]:
        """Get all signals with pagination"""
        return db.query(TradingSignal).order_by(TradingSignal.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_signals_by_status(db: Session, status: SignalStatus) -> List[TradingSignal]:
        """Get signals by status"""
        return db.query(TradingSignal).filter(TradingSignal.status == status).order_by(TradingSignal.timestamp.desc()).all()
    
    @staticmethod
    def get_active_signals(db: Session) -> List[TradingSignal]:
        """Get all active trades"""
        return db.query(TradingSignal).filter(TradingSignal.status == SignalStatus.ACTIVE).all()
    
    @staticmethod
    def get_signals_by_symbol(db: Session, symbol: str) -> List[TradingSignal]:
        """Get signals for a specific symbol"""
        return db.query(TradingSignal).filter(TradingSignal.symbol == symbol).order_by(TradingSignal.timestamp.desc()).all()
    
    @staticmethod
    def get_signals_by_date_range(db: Session, start_date: datetime, end_date: datetime) -> List[TradingSignal]:
        """Get signals within a date range"""
        return db.query(TradingSignal).filter(
            and_(
                TradingSignal.timestamp >= start_date,
                TradingSignal.timestamp <= end_date
            )
        ).order_by(TradingSignal.timestamp.desc()).all()
    
    @staticmethod
    def update_signal_status(db: Session, signal_id: int, status: SignalStatus) -> Optional[TradingSignal]:
        """Update signal status"""
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        if signal:
            signal.status = status
            signal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(signal)
        return signal
    
    @staticmethod
    def enter_trade(db: Session, signal_id: int, entry_price: float, position_size: float = None) -> Optional[TradingSignal]:
        """Mark signal as entered with actual entry price"""
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        if signal:
            signal.status = SignalStatus.ACTIVE
            signal.entry_time = datetime.utcnow()
            signal.entry_price = entry_price
            if position_size:
                signal.position_size = position_size
            
            # Calculate slippage
            if signal.entry:
                signal.slippage = abs(entry_price - signal.entry) * 10000  # Convert to pips
            
            signal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(signal)
        return signal
    
    @staticmethod
    def close_trade(
        db: Session, 
        signal_id: int, 
        exit_price: float, 
        outcome: TradeOutcome,
        pnl: float = None
    ) -> Optional[TradingSignal]:
        """Close a trade with exit price and outcome"""
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        if signal:
            signal.status = SignalStatus.CLOSED
            signal.exit_time = datetime.utcnow()
            signal.exit_price = exit_price
            signal.outcome = outcome
            
            # Calculate duration
            if signal.entry_time:
                duration = signal.exit_time - signal.entry_time
                signal.duration_hours = duration.total_seconds() / 3600
            
            # Calculate pips captured
            if signal.entry_price:
                pips_diff = (exit_price - signal.entry_price) * 10000
                signal.pips_captured = pips_diff if signal.direction == 'BUY' else -pips_diff
            
            # Set P&L
            if pnl is not None:
                signal.actual_pnl = pnl
            
            signal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(signal)
        return signal
    
    @staticmethod
    def update_trade_metrics(
        db: Session,
        signal_id: int,
        mae: float = None,
        mfe: float = None,
        notes: str = None
    ) -> Optional[TradingSignal]:
        """Update trade metrics during or after trade"""
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        if signal:
            if mae is not None:
                signal.mae = mae
            if mfe is not None:
                signal.mfe = mfe
            if notes:
                signal.notes = notes
            signal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(signal)
        return signal
    
    @staticmethod
    def delete_signal(db: Session, signal_id: int) -> bool:
        """Delete a signal"""
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        if signal:
            db.delete(signal)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_statistics(db: Session, days: int = 30) -> Dict:
        """Get trading statistics for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all closed signals in the period
        signals = db.query(TradingSignal).filter(
            and_(
                TradingSignal.timestamp >= start_date,
                TradingSignal.status == SignalStatus.CLOSED
            )
        ).all()
        
        if not signals:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'expectancy': 0,
            }
        
        winners = [s for s in signals if s.outcome == TradeOutcome.WIN]
        losers = [s for s in signals if s.outcome == TradeOutcome.LOSS]
        
        total_wins = len(winners)
        total_losses = len(losers)
        total_trades = len(signals)
        
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(s.actual_pnl for s in signals if s.actual_pnl)
        gross_profit = sum(s.actual_pnl for s in winners if s.actual_pnl) if winners else 0
        gross_loss = abs(sum(s.actual_pnl for s in losers if s.actual_pnl)) if losers else 0
        
        avg_win = gross_profit / total_wins if total_wins > 0 else 0
        avg_loss = gross_loss / total_losses if total_losses > 0 else 0
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        return {
            'total_trades': total_trades,
            'winning_trades': total_wins,
            'losing_trades': total_losses,
            'breakeven_trades': total_trades - total_wins - total_losses,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(max([s.actual_pnl for s in winners if s.actual_pnl], default=0), 2),
            'largest_loss': round(min([s.actual_pnl for s in losers if s.actual_pnl], default=0), 2),
            'profit_factor': round(profit_factor, 2),
            'expectancy': round(expectancy, 2),
            'avg_duration': round(sum(s.duration_hours for s in signals if s.duration_hours) / total_trades, 2) if total_trades > 0 else 0,
        }
    
    @staticmethod
    def get_symbol_performance(db: Session, days: int = 30) -> Dict[str, Dict]:
        """Get performance statistics by symbol"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        signals = db.query(TradingSignal).filter(
            and_(
                TradingSignal.timestamp >= start_date,
                TradingSignal.status == SignalStatus.CLOSED
            )
        ).all()
        
        symbol_stats = {}
        for symbol in set(s.symbol for s in signals):
            symbol_signals = [s for s in signals if s.symbol == symbol]
            winners = [s for s in symbol_signals if s.outcome == TradeOutcome.WIN]
            
            total_trades = len(symbol_signals)
            total_pnl = sum(s.actual_pnl for s in symbol_signals if s.actual_pnl)
            win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0
            
            symbol_stats[symbol] = {
                'trades': total_trades,
                'pnl': round(total_pnl, 2),
                'win_rate': round(win_rate, 2),
                'wins': len(winners),
                'losses': len([s for s in symbol_signals if s.outcome == TradeOutcome.LOSS]),
            }
        
        return symbol_stats


class AnalyticsCRUD:
    """Database operations for trade analytics"""
    
    @staticmethod
    def create_daily_analytics(db: Session, date: datetime = None) -> TradeAnalytics:
        """Generate and save daily analytics"""
        if date is None:
            date = datetime.utcnow()
        
        # Get statistics for the day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        signals = db.query(TradingSignal).filter(
            and_(
                TradingSignal.timestamp >= start_of_day,
                TradingSignal.timestamp < end_of_day,
                TradingSignal.status == SignalStatus.CLOSED
            )
        ).all()
        
        if not signals:
            return None
        
        stats = SignalCRUD.get_statistics(db, days=1)
        symbol_perf = SignalCRUD.get_symbol_performance(db, days=1)
        
        # Find best/worst symbols
        best_symbol = max(symbol_perf.items(), key=lambda x: x[1]['pnl'])[0] if symbol_perf else None
        worst_symbol = min(symbol_perf.items(), key=lambda x: x[1]['pnl'])[0] if symbol_perf else None
        
        analytics = TradeAnalytics(
            date=date,
            total_trades=stats['total_trades'],
            winning_trades=stats['winning_trades'],
            losing_trades=stats['losing_trades'],
            breakeven_trades=stats['breakeven_trades'],
            win_rate=stats['win_rate'],
            profit_factor=stats['profit_factor'],
            total_pnl=stats['total_pnl'],
            gross_profit=stats['gross_profit'],
            gross_loss=stats['gross_loss'],
            avg_win=stats['avg_win'],
            avg_loss=stats['avg_loss'],
            largest_win=stats['largest_win'],
            largest_loss=stats['largest_loss'],
            expectancy=stats['expectancy'],
            avg_duration=stats['avg_duration'],
            best_symbol=best_symbol,
            worst_symbol=worst_symbol,
        )
        
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics
    
    @staticmethod
    def get_analytics_by_date_range(db: Session, start_date: datetime, end_date: datetime) -> List[TradeAnalytics]:
        """Get analytics for a date range"""
        return db.query(TradeAnalytics).filter(
            and_(
                TradeAnalytics.date >= start_date,
                TradeAnalytics.date <= end_date
            )
        ).order_by(TradeAnalytics.date.desc()).all()
    
    @staticmethod
    def get_signals_by_date(db: Session, date) -> List[TradingSignal]:
        """Get signals for a specific date"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        return db.query(TradingSignal).filter(
            and_(
                TradingSignal.timestamp >= start_date,
                TradingSignal.timestamp <= end_date
            )
        ).order_by(TradingSignal.timestamp.desc()).all()
    
    @staticmethod
    def get_latest_signal_by_symbol(db: Session, symbol: str) -> Optional[TradingSignal]:
        """Get the latest signal for a specific symbol"""
        return db.query(TradingSignal).filter(
            TradingSignal.symbol == symbol
        ).order_by(TradingSignal.timestamp.desc()).first()
