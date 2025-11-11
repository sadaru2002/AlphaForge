"""
Enhanced Data Package Builder
Builds comprehensive data packages with deep historical context for Gemini Pro analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class DataPackageBuilder:
    """Builds comprehensive data packages for Gemini Pro analysis"""
    
    @staticmethod
    def build_complete_package(
        symbol: str,
        all_data: Dict[str, pd.DataFrame],
        mtf_analysis: Dict,
        order_blocks: List[Dict],
        fvgs: List[Dict],
        market_structure: Dict,
        liquidity_sweeps: List[Dict],
        premium_discount: Dict,
        ote_zones: List[Dict],
        volume_analysis: Dict,
        technical_indicators: Dict = None
    ) -> Dict[str, Any]:
        """
        Build comprehensive data package with all analysis results
        
        Args:
            symbol: Trading symbol
            all_data: Dict of {timeframe: DataFrame} with OHLCV data
            mtf_analysis: Multi-timeframe trend analysis
            order_blocks: Detected order blocks
            fvgs: Fair Value Gaps
            market_structure: Market structure analysis
            liquidity_sweeps: Detected liquidity sweeps
            premium_discount: Premium/Discount zone analysis
            ote_zones: Optimal Trade Entry zones
            volume_analysis: Volume profile analysis
            technical_indicators: Technical indicator values
            
        Returns:
            Comprehensive data package dict for Gemini
        """
        
        package = {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            
            # ═══════════════════════════════════════════════════════════
            # HISTORICAL PRICE DATA (Deep Context for Gemini)
            # ═══════════════════════════════════════════════════════════
            "price_history": DataPackageBuilder._build_price_history(all_data),
            
            # ═══════════════════════════════════════════════════════════
            # TECHNICAL ANALYSIS
            # ═══════════════════════════════════════════════════════════
            "technical_indicators": technical_indicators or {},
            
            # ═══════════════════════════════════════════════════════════
            # MULTI-TIMEFRAME TREND ANALYSIS
            # ═══════════════════════════════════════════════════════════
            "trend_analysis": {
                "d1_bias": mtf_analysis.get("d1_bias", "neutral"),
                "h4_trend": mtf_analysis.get("h4_trend", "neutral"),
                "h1_momentum": mtf_analysis.get("h1_momentum", "neutral"),
                "m15_setup": mtf_analysis.get("m15_setup", "neutral"),
                "confluence_score": mtf_analysis.get("confluence_score", 0),
                "trend_alignment": mtf_analysis.get("alignment", "weak"),
                "reversal_probability": mtf_analysis.get("reversal_probability", 0),
            },
            
            # ═══════════════════════════════════════════════════════════
            # SMC - SUPPLY & DEMAND ANALYSIS
            # ═══════════════════════════════════════════════════════════
            "smc_analysis": {
                "order_blocks": DataPackageBuilder._format_patterns(order_blocks),
                "fair_value_gaps": DataPackageBuilder._format_patterns(fvgs),
                "liquidity_sweeps": DataPackageBuilder._format_patterns(liquidity_sweeps),
                "optimal_trade_entry": DataPackageBuilder._format_patterns(ote_zones),
            },
            
            # ═══════════════════════════════════════════════════════════
            # ICT - INSTITUTIONAL ORDER FLOW ANALYSIS
            # ═══════════════════════════════════════════════════════════
            "ict_analysis": {
                "market_structure": market_structure,
                "premium_discount_zones": premium_discount,
                "kill_zone_analysis": DataPackageBuilder._analyze_kill_zones(),
                "liquidity_pool_locations": DataPackageBuilder._identify_liquidity_pools(all_data),
                "order_flow_bias": DataPackageBuilder._determine_order_flow(all_data),
            },
            
            # ═══════════════════════════════════════════════════════════
            # VOLUME ANALYSIS
            # ═══════════════════════════════════════════════════════════
            "volume_analysis": volume_analysis,
            
            # ═══════════════════════════════════════════════════════════
            # CURRENT MARKET CONTEXT
            # ═══════════════════════════════════════════════════════════
            "current_candle": DataPackageBuilder._get_current_candle(all_data),
            
            # ═══════════════════════════════════════════════════════════
            # STATISTICAL METRICS
            # ═══════════════════════════════════════════════════════════
            "statistics": DataPackageBuilder._calculate_statistics(all_data),
        }
        
        return package
    
    @staticmethod
    def _build_price_history(all_data: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """
        Build deep price history for context
        Sends good amount of historical data as requested
        """
        history = {}
        
        for timeframe, df in all_data.items():
            if df is None or df.empty:
                continue
            
            # Convert to list of dicts for JSON serialization
            candles = []
            
            # Get last 100 candles for deep context (or whatever available)
            history_slice = df.tail(100) if len(df) > 100 else df
            
            for idx, row in history_slice.iterrows():
                candle = {
                    "time": str(row['time']),
                    "open": float(row.get('open', 0)),
                    "high": float(row.get('high', 0)),
                    "low": float(row.get('low', 0)),
                    "close": float(row.get('close', 0)),
                    "volume": int(row.get('volume', 0)),
                }
                
                # Include technical indicators if available
                for col in df.columns:
                    if col.lower() in ['ema20', 'ema50', 'ema200', 'rsi', 'macd', 'signal', 'histogram', 
                                       'atr', 'bb_upper', 'bb_middle', 'bb_lower', 'adx', 'stoch_k', 'stoch_d']:
                        candle[col] = float(row.get(col, 0)) if pd.notna(row.get(col)) else None
                
                candles.append(candle)
            
            history[timeframe] = {
                "total_candles": len(df),
                "candles_sent": len(candles),
                "data": candles
            }
        
        logger.info(f"Built price history with deep context: {[(tf, h['candles_sent']) for tf, h in history.items()]}")
        return history
    
    @staticmethod
    def _get_current_candle(all_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Get current candle for M15, H1, H4, D1"""
        current = {}
        
        for tf in ['M15', 'H1', 'H4', 'D1']:
            if tf in all_data and not all_data[tf].empty:
                latest = all_data[tf].iloc[-1]
                current[tf] = {
                    "open": float(latest.get('open', 0)),
                    "high": float(latest.get('high', 0)),
                    "low": float(latest.get('low', 0)),
                    "close": float(latest.get('close', 0)),
                    "volume": int(latest.get('volume', 0)),
                    "time": str(latest.get('time', '')),
                }
        
        return current
    
    @staticmethod
    def _calculate_statistics(all_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Calculate statistical metrics across timeframes"""
        stats = {}
        
        for tf, df in all_data.items():
            if df is None or df.empty:
                continue
            
            # Calculate returns
            returns = df['close'].pct_change()
            
            stats[tf] = {
                "volatility": float(returns.std() * 100),  # As percentage
                "average_range": float((df['high'] - df['low']).mean()),
                "average_volume": float(df['volume'].mean()),
                "atr_percentage": float(((df['high'] - df['low']) / df['close'] * 100).mean()),
                "highest_price": float(df['high'].max()),
                "lowest_price": float(df['low'].min()),
                "price_range": float(df['high'].max() - df['low'].min()),
                "win_rate_long": float((df['close'] > df['open']).sum() / len(df) * 100),
                "consecutive_up": int(max(((df['close'] > df['open']).rolling(window=10).sum()).max(), 0)),
                "consecutive_down": int(max(((df['close'] < df['open']).rolling(window=10).sum()).max(), 0)),
            }
        
        return stats
    
    @staticmethod
    def _format_patterns(patterns: List[Dict]) -> List[Dict]:
        """Format pattern data for JSON"""
        formatted = []
        
        for pattern in patterns:
            formatted_pattern = {}
            for key, value in pattern.items():
                if isinstance(value, (int, float, str, bool, list, dict)):
                    formatted_pattern[key] = value
                elif pd.isna(value):
                    formatted_pattern[key] = None
                else:
                    formatted_pattern[key] = str(value)
            formatted.append(formatted_pattern)
        
        return formatted
    
    @staticmethod
    def _analyze_kill_zones() -> Dict[str, Dict]:
        """Analyze trading kill zones (London, New York)"""
        now = datetime.now(timezone.utc)
        
        # London session: 07:00-10:00 UTC
        london_start = now.replace(hour=7, minute=0, second=0, microsecond=0)
        london_end = now.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # New York session: 13:00-16:00 UTC
        ny_start = now.replace(hour=13, minute=0, second=0, microsecond=0)
        ny_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return {
            "london": {
                "active": london_start <= now <= london_end,
                "start": "07:00 UTC",
                "end": "10:00 UTC",
                "status": "active" if london_start <= now <= london_end else "upcoming/closed"
            },
            "new_york": {
                "active": ny_start <= now <= ny_end,
                "start": "13:00 UTC",
                "end": "16:00 UTC",
                "status": "active" if ny_start <= now <= ny_end else "upcoming/closed"
            }
        }
    
    @staticmethod
    def _identify_liquidity_pools(all_data: Dict[str, pd.DataFrame]) -> Dict[str, List[float]]:
        """Identify major liquidity pool locations"""
        pools = {}
        
        if 'D1' in all_data and not all_data['D1'].empty:
            d1_data = all_data['D1'].tail(50)
            
            # Previous day high/low (often liquidity)
            pools['previous_day_high'] = float(d1_data.iloc[-2]['high']) if len(d1_data) > 1 else None
            pools['previous_day_low'] = float(d1_data.iloc[-2]['low']) if len(d1_data) > 1 else None
            
            # Weekly highs/lows
            pools['recent_high'] = float(d1_data['high'].max())
            pools['recent_low'] = float(d1_data['low'].min())
        
        return pools
    
    @staticmethod
    def _determine_order_flow(all_data: Dict[str, pd.DataFrame]) -> str:
        """Determine institutional order flow bias"""
        if 'H4' in all_data and not all_data['H4'].empty:
            h4_recent = all_data['H4'].tail(5)
            
            # Simple order flow: compare closes to opens
            up_candles = (h4_recent['close'] > h4_recent['open']).sum()
            
            if up_candles >= 4:
                return "bullish"
            elif up_candles <= 1:
                return "bearish"
            else:
                return "mixed"
        
        return "neutral"
    
    @staticmethod
    def create_gemini_context_string(package: Dict) -> str:
        """
        Create human-readable context string for Gemini prompt
        Ensures rich historical context is properly formatted
        """
        context = []
        
        # Price History Summary
        context.append("=== PRICE HISTORY CONTEXT ===")
        for tf, hist in package.get('price_history', {}).items():
            context.append(f"{tf}: {hist['candles_sent']} candles (total {hist['total_candles']})")
        
        # Current Candles
        context.append("\n=== CURRENT CANDLES ===")
        for tf, candle in package.get('current_candle', {}).items():
            context.append(f"{tf}: O:{candle['open']:.5f} H:{candle['high']:.5f} L:{candle['low']:.5f} C:{candle['close']:.5f}")
        
        # Trend Analysis
        trend = package.get('trend_analysis', {})
        context.append(f"\n=== TREND ANALYSIS ===")
        context.append(f"D1 Bias: {trend.get('d1_bias', 'unknown')}")
        context.append(f"H4 Trend: {trend.get('h4_trend', 'unknown')}")
        context.append(f"H1 Momentum: {trend.get('h1_momentum', 'unknown')}")
        context.append(f"M15 Setup: {trend.get('m15_setup', 'unknown')}")
        context.append(f"Confluence Score: {trend.get('confluence_score', 0)}/100")
        
        # SMC Analysis
        smc = package.get('smc_analysis', {})
        context.append(f"\n=== SMC SUPPLY & DEMAND ===")
        context.append(f"Order Blocks: {len(smc.get('order_blocks', []))}")
        context.append(f"Fair Value Gaps: {len(smc.get('fair_value_gaps', []))}")
        context.append(f"Liquidity Sweeps: {len(smc.get('liquidity_sweeps', []))}")
        
        # Volume Analysis
        volume = package.get('volume_analysis', {})
        context.append(f"\n=== VOLUME ANALYSIS ===")
        context.append(f"Current Volume: {volume.get('current_volume', 'N/A')}")
        context.append(f"Average Volume: {volume.get('average_volume', 'N/A')}")
        context.append(f"Volume Trend: {volume.get('volume_trend', 'unknown')}")
        
        return "\n".join(context)
