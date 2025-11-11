"""
Enhanced Signal Generator with Gemini AI Confirmation
=====================================================
NEW WORKFLOW:
1-7. Technical Analysis (AlphaForge Strategy)
8-9. Send to Gemini AI for Confirmation
10. Gemini validates and optimizes SL/TP
11. Display confirmed signal on Frontend UI
12. User manually adds to Trading Journal
13. System auto-calculates analytics from Journal
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AlphaForge Strategy Components
from alphaforge_strategy import (
    OandaConfig, StrategyConfig, DataHandler, 
    StrategyEngine, TechnicalIndicators
)
import strategy_variables as config

# Gemini AI Validation
from gemini.simple_validator import GeminiSignalValidator

# Database
from database.database import SessionLocal
from database.signal_crud import SignalCRUD
from database.signal_models import SignalStatus

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedSignalGenerator:
    """
    Enhanced Signal Generator with Gemini AI Confirmation
    
    Workflow:
    --------
    1. Detect technical setup (AlphaForge)
    2. Gather multi-timeframe data
    3. Send complete analysis package to Gemini AI
    4. Gemini confirms signal + provides optimized SL/TP
    5. Save to database
    6. Frontend displays signal
    7. User adds to journal manually
    8. System calculates analytics from journal
    """
    
    def __init__(self):
        """Initialize enhanced signal generator"""
        logger.info("🚀 Initializing Enhanced Signal Generator with Gemini AI...")
        
        # Initialize database
        self._init_database()
        
        # AlphaForge Components
        self.oanda_config = OandaConfig(
            config.OANDA_ACCESS_TOKEN,
            config.OANDA_ACCOUNT_ID,
            config.OANDA_ENVIRONMENT
        )
        self.strategy_config = StrategyConfig()
        self.data_handler = DataHandler(self.oanda_config)
        self.strategy_engine = StrategyEngine(self.strategy_config)
        
        # Gemini AI Validator
        try:
            self.gemini_validator = GeminiSignalValidator()
            self.use_gemini = self.gemini_validator.enabled
            if self.use_gemini:
                logger.info("✅ Gemini AI confirmation ENABLED")
            else:
                logger.info("⚠️ Gemini AI unavailable - signals will be auto-approved")
        except Exception as e:
            logger.warning(f"⚠️ Gemini initialization failed: {e}")
            self.use_gemini = False
        
        # Configuration
        self.instruments = config.INSTRUMENTS
        self.timeframe = config.TIMEFRAME
        self.lookback_bars = 500
        
        # Signal tracking
        self.last_signal_time = {}
        self.cooldown_minutes = 15  # Minimum time between signals per instrument
        # Gemini throttle tracking to avoid rapid repeated API calls
        self._last_gemini_call_ts = None
        
        logger.info(f"✅ Initialized for instruments: {', '.join(self.instruments)}")
    
    def _init_database(self):
        """Initialize signal database"""
        try:
            from sqlalchemy import create_engine
            from database.signal_models import Base as SignalBase
            
            # Get database URL from environment
            database_url = os.getenv("DATABASE_URL", "sqlite:///./trading_signals.db")
            
            # Configure engine based on database type
            if database_url.startswith('postgresql'):
                engine = create_engine(
                    database_url,
                    pool_pre_ping=True,
                    pool_recycle=300
                )
            else:
                engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False}
                )
            
            SignalBase.metadata.create_all(bind=engine)
            logger.info("✅ Signal database initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization warning: {e}")
    
    # ========================================================================
    # STEP 1-7: TECHNICAL ANALYSIS (AlphaForge Strategy)
    # ========================================================================
    
    def detect_technical_setup(self, instrument: str, df: pd.DataFrame) -> Optional[Dict]:
        """
        Steps 1-7: Detect trading setup using AlphaForge strategy
        
        Returns:
            Raw signal dictionary if setup detected, None otherwise
        """
        try:
            logger.info(f"📊 Running technical analysis on {instrument}...")
            
            # Add all indicators
            df = self.strategy_engine.add_indicators(df)
            df = self.strategy_engine.apply_filters(df)
            df = self.strategy_engine.generate_signals(df)
            
            if df.empty or len(df) < 2:
                return None
            
            # Check for signal triggers
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            # Detect signal direction
            signal_direction = None
            
            # Check long trigger
            if last_row.get('long_trigger', False) and not prev_row.get('long_trigger', False):
                signal_direction = 'BUY'
            # Check short trigger
            elif last_row.get('short_trigger', False) and not prev_row.get('short_trigger', False):
                signal_direction = 'SELL'
            
            if signal_direction is None:
                logger.info(f"ℹ️ No signal detected for {instrument}")
                return None
            
            # Extract technical data
            current_price = last_row['close']
            atr = last_row.get('atr', 0.001)
            rsi = last_row.get('rsi', 50)
            ema_200 = last_row.get('ema_200', current_price)
            
            # Calculate initial SL/TP (Gemini will optimize these)
            if signal_direction == 'BUY':
                stop_loss = current_price - (2 * atr)
                tp1 = current_price + (2 * atr)
                tp2 = current_price + (4 * atr)
                tp3 = current_price + (6 * atr)
            else:
                stop_loss = current_price + (2 * atr)
                tp1 = current_price - (2 * atr)
                tp2 = current_price - (4 * atr)
                tp3 = current_price - (6 * atr)
            
            # Determine market condition
            market_condition = "TRENDING_UP" if current_price > ema_200 else "TRENDING_DOWN"
            
            # Determine session
            hour = datetime.now().hour
            if 7 <= hour < 16:
                session = "LONDON"
            elif 13 <= hour < 22:
                session = "NEW_YORK"
            else:
                session = "ASIAN"
            
            raw_signal = {
                'instrument': instrument,
                'direction': signal_direction,
                'entry_price': round(current_price, 5),
                'stop_loss': round(stop_loss, 5),
                'tp1': round(tp1, 5),
                'tp2': round(tp2, 5),
                'tp3': round(tp3, 5),
                'atr': round(atr, 5),
                'rsi': round(rsi, 2),
                'market_condition': market_condition,
                'session': session,
                'timestamp': datetime.now(),
                'technical_data': {
                    'close': current_price,
                    'ema_200': ema_200,
                    'volume': last_row.get('volume', 0),
                    'adx': last_row.get('adx', 0)
                }
            }
            
            logger.info(f"✅ Setup detected: {instrument} {signal_direction} @ {current_price:.5f}")
            return raw_signal
            
        except Exception as e:
            logger.error(f"❌ Error in technical analysis: {e}")
            return None
    
    # ========================================================================
    # STEP 8-9: GEMINI AI CONFIRMATION
    # ========================================================================
    
    def fetch_multi_timeframe_data(self, instrument: str) -> Dict[str, pd.DataFrame]:
        """Fetch data from multiple timeframes for comprehensive analysis"""
        try:
            logger.info(f"📊 Fetching multi-timeframe data for {instrument}...")
            
            timeframes = {
                'M5': 500,   # Primary timeframe
                'M15': 300,  # 3 days
                'H1': 200,   # 8 days
                'H4': 150,   # 25 days
                'D1': 100    # 100 days
            }
            
            mtf_data = {}
            
            for tf, bars in timeframes.items():
                try:
                    df = self.data_handler.fetch_historical_data(instrument, tf, bars)
                    if df is not None and not df.empty:
                        # Add indicators
                        df = self.strategy_engine.add_indicators(df)
                        mtf_data[tf] = df
                        logger.info(f"  ✓ {tf}: {len(df)} bars")
                except Exception as e:
                    logger.warning(f"  ✗ {tf}: {e}")
            
            return mtf_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching MTF data: {e}")
            return {}
    
    def prepare_gemini_package(self, raw_signal: Dict, mtf_data: Dict) -> Dict:
        """
        Prepare comprehensive analysis package for Gemini AI
        Includes all technical indicators, price action, and multi-timeframe context
        """
        try:
            instrument = raw_signal['instrument']
            
            # Extract latest indicators from each timeframe
            latest_indicators = {}
            for tf, df in mtf_data.items():
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    latest_indicators[tf] = {
                        'close': float(latest.get('close', 0)),
                        'open': float(latest.get('open', 0)),
                        'high': float(latest.get('high', 0)),
                        'low': float(latest.get('low', 0)),
                        'rsi': float(latest.get('rsi', 50)),
                        'atr': float(latest.get('atr', 0)),
                        'ema_50': float(latest.get('ema_50', latest.get('close', 0))),
                        'ema_200': float(latest.get('ema_200', latest.get('close', 0))),
                        'adx': float(latest.get('adx', 0)),
                        'volume': int(latest.get('volume', 0))
                    }
            
            # Trend alignment across timeframes
            trend_alignment = {}
            for tf, df in mtf_data.items():
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    close = latest.get('close', 0)
                    ema_200 = latest.get('ema_200', close)
                    trend_alignment[tf] = "BULLISH" if close > ema_200 else "BEARISH"
            
            # Support/Resistance levels
            sr_levels = {}
            for tf in ['H4', 'D1']:
                if tf in mtf_data and mtf_data[tf] is not None:
                    df = mtf_data[tf].tail(50)
                    sr_levels[tf] = {
                        'resistance_levels': df['high'].nlargest(3).tolist(),
                        'support_levels': df['low'].nsmallest(3).tolist()
                    }
            
            # Price history (recent candles)
            price_history = {}
            for tf, df in mtf_data.items():
                if df is not None and not df.empty:
                    recent = df.tail(20)
                    price_history[tf] = {
                        'highs': recent['high'].tolist(),
                        'lows': recent['low'].tolist(),
                        'closes': recent['close'].tolist(),
                        'opens': recent['open'].tolist()
                    }
            
            # Build complete package
            package = {
                'symbol': instrument,
                'detected_setup': {
                    'direction': raw_signal['direction'],
                    'entry_price': raw_signal['entry_price'],
                    'detection_timeframe': 'M5',
                    'timestamp': raw_signal['timestamp'].isoformat()
                },
                'multi_timeframe_indicators': latest_indicators,
                'trend_alignment': trend_alignment,
                'support_resistance': sr_levels,
                'price_history': price_history,
                'current_market_state': {
                    'session': raw_signal['session'],
                    'volatility': raw_signal['atr'],
                    'market_condition': raw_signal['market_condition'],
                    'rsi': raw_signal['rsi']
                },
                'initial_levels': {
                    'stop_loss': raw_signal['stop_loss'],
                    'tp1': raw_signal['tp1'],
                    'tp2': raw_signal['tp2'],
                    'tp3': raw_signal['tp3']
                },
                'request': {
                    'analyze_setup': True,
                    'optimize_sl_tp': True,
                    'confidence_threshold': 60,
                    'min_risk_reward': 2.0
                }
            }
            
            logger.info(f"📦 Gemini package prepared with {len(mtf_data)} timeframes")
            return package
            
        except Exception as e:
            logger.error(f"❌ Error preparing Gemini package: {e}")
            return {}
    
    def confirm_with_gemini(self, raw_signal: Dict) -> Optional[Dict]:
        """
        Steps 8-10: Send signal to Gemini AI for confirmation and optimization
        
        Returns:
            Confirmed signal with Gemini's analysis, or None if rejected
        """
        try:
            instrument = raw_signal['instrument']
            
            if not self.use_gemini:
                logger.info(f"📊 Auto-approving signal (Gemini disabled)")
                return self._auto_approve_signal(raw_signal)
            
            logger.info(f"🤖 Requesting Gemini AI confirmation for {instrument}...")

            # Quick local quality check BEFORE calling Gemini to reduce API usage
            try:
                if getattr(config, 'GEMINI_LOCAL_FILTER_ENABLED', True):
                    passed = self._quick_quality_check(raw_signal)
                    if not passed:
                        logger.info("ℹ️ Local quality check failed — skipping Gemini and auto-approving strategy levels")
                        return self._auto_approve_signal(raw_signal)
            except Exception as e:
                logger.warning(f"⚠️ Local quality check error: {e} — continuing to Gemini")

            # Respect simple throttling between Gemini calls (extra protection vs quotas)
            try:
                throttle_sec = getattr(config, 'GEMINI_THROTTLE_SECONDS', 0)
                if throttle_sec and self._last_gemini_call_ts is not None:
                    elapsed = (datetime.now() - self._last_gemini_call_ts).total_seconds()
                    if elapsed < throttle_sec:
                        wait = throttle_sec - elapsed
                        logger.info(f"⏳ Throttling Gemini calls: sleeping {wait:.1f}s to respect GEMINI_THROTTLE_SECONDS")
                        time.sleep(wait)
            except Exception:
                # Non-fatal — continue without throttle if something fails
                pass

            # Fetch multi-timeframe data
            mtf_data = self.fetch_multi_timeframe_data(instrument)
            
            if not mtf_data:
                logger.warning(f"⚠️ No MTF data - auto-approving with strategy levels")
                return self._auto_approve_signal(raw_signal)
            
            # Prepare comprehensive package
            gemini_package = self.prepare_gemini_package(raw_signal, mtf_data)
            
            # Build validator-friendly payloads and call Gemini (returns approved, data)
            try:
                signal_for_validator = {
                    'symbol': gemini_package.get('symbol'),
                    'type': gemini_package.get('detected_setup', {}).get('direction'),
                    'entry_price': gemini_package.get('detected_setup', {}).get('entry_price'),
                    'current_price': gemini_package.get('detected_setup', {}).get('entry_price'),
                    'stop_loss': gemini_package.get('initial_levels', {}).get('stop_loss'),
                    'take_profit': gemini_package.get('initial_levels', {}).get('tp1')
                }

                market_analysis = {
                    'rsi': gemini_package.get('current_market_state', {}).get('rsi'),
                    'adx': gemini_package.get('multi_timeframe_indicators', {}).get('M5', {}).get('adx'),
                    'trend': gemini_package.get('trend_alignment', {}).get('M5'),
                    'alma_signal': None,
                    'volume_status': 'HIGH' if gemini_package.get('multi_timeframe_indicators', {}).get('M5', {}).get('volume', 0) > 0 else 'UNKNOWN'
                }

                approved, gemini_data = self.gemini_validator.validate_signal(
                    signal_for_validator,
                    market_analysis,
                    confidence_threshold=0.60
                )

                # Record the last Gemini call timestamp for throttling
                try:
                    self._last_gemini_call_ts = datetime.now()
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"❌ Error calling Gemini validator: {e}")
                return None

            # Interpret Gemini result
            if not approved:
                logger.warning(f"❌ Gemini REJECTED the signal for {instrument}")
                return None

            # If gemini_data is None, validator auto-approved without suggestions — use raw levels
            gs = gemini_data or {}

            # Build confirmed signal (use Gemini optimized values when present)
            confirmed_signal = {
                'symbol': instrument,
                'direction': gs.get('type', raw_signal['direction']) if gs.get('type') else raw_signal['direction'],
                'entry': gs.get('optimized_tp', raw_signal['entry_price']) if gs.get('optimized_tp') else raw_signal['entry_price'],
                'stop_loss': gs.get('optimized_sl', raw_signal['stop_loss']) if gs.get('optimized_sl') else raw_signal['stop_loss'],
                'tp1': gs.get('optimized_tp', raw_signal['tp1']) if gs.get('optimized_tp') else raw_signal['tp1'],
                'tp2': gs.get('tp2', raw_signal['tp2']) if gs.get('tp2') else raw_signal['tp2'],
                'tp3': gs.get('tp3', raw_signal['tp3']) if gs.get('tp3') else raw_signal['tp3'],
                'confidence_score': gs.get('confidence', 70),
                'signal_strength': gs.get('signal_strength', 'MEDIUM'),
                'reasoning': gs.get('reasoning', 'Gemini AI analysis') if gs else 'Gemini auto-approved',
                'market_condition': raw_signal['market_condition'],
                'session': raw_signal['session'],
                'volatility_level': raw_signal['atr'],
                'rsi': raw_signal['rsi'],
                'validated_by': 'GEMINI_AI',
                'timestamp': raw_signal['timestamp']
            }
            
            logger.info(f"✅ Gemini CONFIRMED: {instrument} | Confidence: {confirmed_signal['confidence_score']}%")
            return confirmed_signal
            
        except Exception as e:
            logger.error(f"❌ Gemini confirmation error: {e}")
            return None
    
    def _auto_approve_signal(self, raw_signal: Dict) -> Dict:
        """Auto-approve signal when Gemini is unavailable"""
        return {
            'symbol': raw_signal['instrument'],
            'direction': raw_signal['direction'],
            'entry': raw_signal['entry_price'],
            'stop_loss': raw_signal['stop_loss'],
            'tp1': raw_signal['tp1'],
            'tp2': raw_signal['tp2'],
            'tp3': raw_signal['tp3'],
            'confidence_score': 70,
            'signal_strength': 'MEDIUM',
            'reasoning': 'AlphaForge strategy signal (auto-approved)',
            'market_condition': raw_signal['market_condition'],
            'session': raw_signal['session'],
            'volatility_level': raw_signal['atr'],
            'rsi': raw_signal['rsi'],
            'validated_by': 'STRATEGY',
            'timestamp': raw_signal['timestamp']
        }

    def _quick_quality_check(self, raw_signal: Dict) -> bool:
        """
        Lightweight local scoring to decide whether to call Gemini.
        Returns True if signal is worth sending to Gemini, False otherwise.
        This avoids sending every detected setup to the AI and reduces quota usage.
        """
        try:
            score = 0
            weight_total = 0

            td = raw_signal.get('technical_data', {})
            adx = float(td.get('adx', 0) or 0)
            volume = float(td.get('volume', 0) or 0)
            atr = float(raw_signal.get('atr', 0) or 0)
            rsi = float(raw_signal.get('rsi', 50) or 50)

            # ADX — trend strength
            adx_threshold = getattr(config, 'GEMINI_LOCAL_ADX_THRESHOLD', 20)
            weight_total += 1
            if adx >= adx_threshold:
                score += 1

            # Volume — above average multiplier
            vol_mult = getattr(config, 'GEMINI_LOCAL_VOLUME_MULTIPLIER', 1.2)
            avg_vol = getattr(config, 'GEMINI_LOCAL_AVG_VOLUME', None)
            # If average unknown, assume pass if raw volume > 0
            weight_total += 1
            if avg_vol is None:
                if volume > 0:
                    score += 1
            else:
                if volume >= avg_vol * vol_mult:
                    score += 1

            # RSI in favorable range
            rsi_min = getattr(config, 'GEMINI_LOCAL_RSI_MIN', 45)
            rsi_max = getattr(config, 'GEMINI_LOCAL_RSI_MAX', 65)
            weight_total += 1
            if rsi_min <= rsi <= rsi_max:
                score += 1

            # Volatility check (avoid tiny ATR setups)
            atr_min = getattr(config, 'GEMINI_LOCAL_ATR_MIN', 0.0001)
            weight_total += 1
            if atr >= atr_min:
                score += 1

            # Compute normalized score
            threshold = getattr(config, 'GEMINI_LOCAL_SCORE_THRESHOLD', 3)
            logger.debug(f"Local quality score: {score}/{weight_total} (threshold {threshold})")
            return score >= threshold
        except Exception as e:
            logger.warning(f"⚠️ Quick quality check failed: {e}")
            return True
    
    # ========================================================================
    # STEP 11: SAVE TO DATABASE FOR FRONTEND DISPLAY
    # ========================================================================
    
    def save_confirmed_signal(self, confirmed_signal: Dict) -> Optional[int]:
        """
        Step 11: Save confirmed signal to database
        Frontend will display this signal
        User can then manually add to journal
        
        Returns:
            Signal ID if saved successfully, None otherwise
        """
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from database.signal_models import Base as SignalBase
            
            # Get database URL from environment
            database_url = os.getenv("DATABASE_URL", "sqlite:///./trading_signals.db")
            
            # Configure engine based on database type
            if database_url.startswith('postgresql'):
                engine = create_engine(
                    database_url,
                    pool_pre_ping=True,
                    pool_recycle=300
                )
            else:
                engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False}
                )
            
            SignalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SignalSessionLocal()
            
            # Create signal
            signal = SignalCRUD.create_signal(db, confirmed_signal)
            signal_id = signal.id
            
            db.close()
            
            logger.info(f"💾 Signal saved to database: ID={signal_id} | {confirmed_signal['symbol']} {confirmed_signal['direction']}")
            logger.info(f"📱 Signal now visible on Frontend UI - User can add to journal")
            
            return signal_id
            
        except Exception as e:
            logger.error(f"❌ Error saving signal: {e}")
            return None
    
    # ========================================================================
    # MAIN WORKFLOW
    # ========================================================================
    
    def process_instrument(self, instrument: str) -> bool:
        """
        Complete workflow for one instrument:
        1-7.  Detect technical setup (AlphaForge)
        8-10. Confirm with Gemini AI
        11.   Save to database
        12.   Frontend displays signal
        13.   User adds to journal → system calculates analytics
        
        Returns:
            True if signal generated and confirmed, False otherwise
        """
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"🔍 Processing {instrument}...")
            logger.info(f"{'='*70}")
            
            # Check cooldown
            if instrument in self.last_signal_time:
                elapsed = (datetime.now() - self.last_signal_time[instrument]).total_seconds() / 60
                if elapsed < self.cooldown_minutes:
                    logger.info(f"⏳ Cooldown active: {elapsed:.1f}/{self.cooldown_minutes} min")
                    return False
            
            # Fetch data
            df = self.data_handler.fetch_historical_data(
                instrument,
                self.timeframe,
                self.lookback_bars
            )
            
            if df.empty:
                logger.warning(f"⚠️ No data received for {instrument}")
                return False
            
            logger.info(f"✅ Fetched {len(df)} bars of data")
            
            # STEPS 1-7: Technical Analysis
            raw_signal = self.detect_technical_setup(instrument, df)
            
            if raw_signal is None:
                logger.info(f"ℹ️ No technical setup detected")
                return False
            
            # STEPS 8-10: Gemini Confirmation
            confirmed_signal = self.confirm_with_gemini(raw_signal)
            
            if confirmed_signal is None:
                logger.info(f"❌ Signal not confirmed by Gemini")
                return False
            
            # STEP 11: Save to Database
            signal_id = self.save_confirmed_signal(confirmed_signal)
            
            if signal_id:
                self.last_signal_time[instrument] = datetime.now()
                
                logger.info(f"\n{'='*70}")
                logger.info(f"🎯 SUCCESS! Signal Generated & Confirmed")
                logger.info(f"{'='*70}")
                logger.info(f"Signal ID: {signal_id}")
                logger.info(f"Symbol: {confirmed_signal['symbol']}")
                logger.info(f"Direction: {confirmed_signal['direction']}")
                logger.info(f"Entry: {confirmed_signal['entry']:.5f}")
                logger.info(f"Stop Loss: {confirmed_signal['stop_loss']:.5f}")
                logger.info(f"Take Profit 2: {confirmed_signal['tp2']:.5f}")
                logger.info(f"Confidence: {confirmed_signal['confidence_score']}%")
                logger.info(f"Validated By: {confirmed_signal['validated_by']}")
                logger.info(f"\n📱 NEXT STEPS:")
                logger.info(f"1. Signal visible on Frontend UI")
                logger.info(f"2. User decides whether to take trade")
                logger.info(f"3. User manually adds to Trading Journal")
                logger.info(f"4. System auto-calculates analytics from Journal")
                logger.info(f"{'='*70}\n")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error processing {instrument}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_continuous(self, scan_interval: int = 60):
        """
        Continuous signal generation loop
        Scans all instruments every N seconds
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 ENHANCED SIGNAL GENERATOR - CONTINUOUS MODE")
        logger.info("="*70)
        logger.info(f"📊 Instruments: {', '.join(self.instruments)}")
        logger.info(f"⏱️  Scan Interval: {scan_interval} seconds")
        logger.info(f"🔒 Cooldown: {self.cooldown_minutes} minutes")
        logger.info(f"🤖 Gemini AI: {'ENABLED' if self.use_gemini else 'DISABLED'}")
        logger.info("="*70 + "\n")
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                logger.info(f"\n🔄 SCAN CYCLE #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                signals_generated = 0
                
                for instrument in self.instruments:
                    if self.process_instrument(instrument):
                        signals_generated += 1
                    time.sleep(2)
                
                logger.info(f"\n📊 Cycle #{cycle} Complete: {signals_generated} new signals")
                logger.info(f"⏳ Next scan in {scan_interval} seconds...\n")
                
                time.sleep(scan_interval)
                
        except KeyboardInterrupt:
            logger.info("\n\n⚠️ Stopped by user")
    
    def run_single_scan(self):
        """Single scan across all instruments"""
        logger.info("\n" + "="*70)
        logger.info("🎯 ENHANCED SIGNAL GENERATOR - SINGLE SCAN")
        logger.info("="*70 + "\n")
        
        results = {}
        
        for instrument in self.instruments:
            results[instrument] = self.process_instrument(instrument)
            time.sleep(2)
        
        logger.info("\n" + "="*70)
        logger.info("📊 SCAN RESULTS:")
        for instrument, success in results.items():
            status = "✅ Signal Generated" if success else "ℹ️  No Signal"
            logger.info(f"  {instrument}: {status}")
        logger.info("="*70 + "\n")
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AlphaForge Enhanced Signal Generator with Gemini AI'
    )
    parser.add_argument(
        'mode',
        choices=['continuous', 'single'],
        help='continuous: Loop forever | single: One scan'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Scan interval in seconds (continuous mode)'
    )
    
    args = parser.parse_args()
    
    # Initialize
    generator = EnhancedSignalGenerator()
    
    # Run
    if args.mode == 'continuous':
        generator.run_continuous(scan_interval=args.interval)
    else:
        generator.run_single_scan()


if __name__ == "__main__":
    main()
