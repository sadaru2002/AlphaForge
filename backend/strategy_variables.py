
"""
AlphaForge Trading Strategy - Editable Variables
Edit this file to customize your trading strategy without touching the main code
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# OANDA API CREDENTIALS (from .env file)
# ============================================================================
OANDA_ACCESS_TOKEN = os.getenv('OANDA_API_KEY')
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')
OANDA_ENVIRONMENT = os.getenv('OANDA_ENVIRONMENT', 'practice')  # "practice" or "live"

# ============================================================================
# TRADING INSTRUMENTS
# ============================================================================
INSTRUMENTS = ["XAU_USD", "GBP_USD", "USD_JPY"]
# Available: XAU_USD (Gold), EUR_USD, GBP_USD, USD_JPY, AUD_USD, etc.

# ============================================================================
# TIMEFRAME SETTINGS
# ============================================================================
TIMEFRAME = "M5"  # M5 for fastest day trading (M1, M5, M15, H1, H4, D1)
LOOKBACK_BARS = 500  # Number of historical bars to fetch (500 M5 bars = ~42 hours)

# ============================================================================
# MOVING AVERAGE SETTINGS
# ============================================================================
BASIS_TYPE = "ALMA"  # ALMA, TEMA, or HullMA
BASIS_LENGTH = 2  # Length of the moving average
OFFSET_SIGMA = 5  # ALMA parameter (higher = smoother)
OFFSET_ALMA = 0.85  # ALMA offset (0.85 = default)
DELAY_OFFSET = 0  # Delay for MA calculation (0 = no delay)

# Alternate Signal Settings
USE_ALTERNATE_SIGNALS = True  # Use higher timeframe signals - CRITICAL FOR QUALITY
ALTERNATE_MULTIPLIER = 12  # Multiplier for alternate timeframe (12 = 60min bars for M5)

# ============================================================================
# RSI SETTINGS
# ============================================================================
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ============================================================================
# FILTER TOGGLES (True = Enabled, False = Disabled)
# ============================================================================
# 🎯 DAY TRADING MODE: 5-10 signals/day with 1:2 RR ratio
# Uses strict filters for quality day trading setups on H1 timeframe

# ATR Filters
ENABLE_ATR_FILTER_1 = False  # ATR normalization filter (disabled)
ENABLE_ATR_FILTER_2 = False  # ATR change filter (disabled)

# Volume Filter
ENABLE_VOLUME_FILTER = True  # ✅ Only trade when volume is above average
VOLUME_MULTIPLIER = 1.2      # ✅ Need 20% above average volume

# RSI & EMA Filter
ENABLE_RSI_EMA_FILTER = False  # Disabled for day trading

# EMA 200 Filter  
ENABLE_EMA_FILTER = True     # ✅ Enabled - Trend alignment is critical
EMA_LENGTH = 200             # Length of EMA filter

# ADX Filter
ENABLE_ADX_FILTER = True     # ✅ Enabled - Need trending markets
ADX_SMOOTHING = 14
ADX_DI_LENGTH = 14
ADX_THRESHOLD = 25           # Minimum ADX value (trend strength)

# Additional RSI Filter
ENABLE_RSI_FILTER = False    # Handled in day trading logic

# Bollinger Bands Filter
ENABLE_BB_FILTER = False     # Disabled for day trading

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
INITIAL_CAPITAL = 5000  # Starting capital
POSITION_SIZE_PCT = 50  # Percentage of equity per trade (1-100)
STOP_LOSS_POINTS = 0  # Stop loss in points (0 = disabled)
TAKE_PROFIT_POINTS = 0  # Take profit in points (0 = disabled)
COMMISSION_PCT = 0.02  # Commission percentage

# ============================================================================
# DEMA ATR SETTINGS
# ============================================================================
USE_HA_CANDLES = True  # Use Heikin Ashi candles
DEMA_PERIOD = 7  # DEMA period
ATR_PERIOD = 14  # ATR period
ATR_FACTOR = 1.7  # ATR multiplication factor

# ============================================================================
# ADDITIONAL SETTINGS
# ============================================================================
USE_MOVING_AVERAGES = False  # Enable MA ribbon
ALMA_MAIN_LENGTH = 423  # Main ALMA length for ribbon

# ============================================================================
# GEMINI LOCAL FILTER / THROTTLING (Controls when to call AI validator)
# ============================================================================
# Only send signals to Gemini when local quick-quality checks pass.
# Tune these to reduce API usage and reserve Gemini calls for the strongest setups.
GEMINI_LOCAL_FILTER_ENABLED = True
# Minimum ADX required to consider calling Gemini (trend strength)
GEMINI_LOCAL_ADX_THRESHOLD = 30
# Volume must be this many times above average to pass (if avg known)
GEMINI_LOCAL_VOLUME_MULTIPLIER = 1.5
# RSI acceptable window for setups to be considered (preference for mid-range RSI)
GEMINI_LOCAL_RSI_MIN = 48
GEMINI_LOCAL_RSI_MAX = 62
# Minimum ATR (in instrument price terms) to avoid sending tiny noise setups
GEMINI_LOCAL_ATR_MIN = 0.0003
# How many of the local checks must pass (out of total) to allow Gemini call
GEMINI_LOCAL_SCORE_THRESHOLD = 4
# Simple throttle (seconds) between Gemini API calls (adds extra protection)
GEMINI_THROTTLE_SECONDS = 2

# ============================================================================
# STRATEGY PRESETS (Quick configurations)
# ============================================================================

def apply_signal_detection_mode():
    """Relaxed thresholds for signal detection with basic quality filters"""
    global ENABLE_ATR_FILTER_1, ENABLE_ATR_FILTER_2, ENABLE_VOLUME_FILTER
    global ENABLE_RSI_EMA_FILTER, ENABLE_EMA_FILTER, ENABLE_ADX_FILTER
    global ENABLE_RSI_FILTER, ENABLE_BB_FILTER, POSITION_SIZE_PCT
    global GEMINI_LOCAL_FILTER_ENABLED, GEMINI_LOCAL_VOLUME_MULTIPLIER
    global GEMINI_LOCAL_ADX_THRESHOLD, GEMINI_LOCAL_RSI_MIN, GEMINI_LOCAL_RSI_MAX
    global GEMINI_LOCAL_SCORE_THRESHOLD
    
    # Extremely relaxed filters for testing
    GEMINI_LOCAL_FILTER_ENABLED = True
    GEMINI_LOCAL_VOLUME_MULTIPLIER = 0.5  # Accept below average volume
    GEMINI_LOCAL_ADX_THRESHOLD = 10  # Minimal trend strength requirement
    GEMINI_LOCAL_RSI_MIN = 20  # Full RSI window
    GEMINI_LOCAL_RSI_MAX = 80
    GEMINI_LOCAL_SCORE_THRESHOLD = 1  # Need only 1 check to pass
    
    # Also disable most other filters for testing
    ENABLE_ATR_FILTER_1 = False
    ENABLE_ATR_FILTER_2 = False
    ENABLE_VOLUME_FILTER = False  # Disable volume filter completely
    ENABLE_RSI_EMA_FILTER = False
    ENABLE_EMA_FILTER = False
    ENABLE_ADX_FILTER = False
    ENABLE_RSI_FILTER = False
    ENABLE_BB_FILTER = False
    
    # Keep only essential filters
    ENABLE_ATR_FILTER_1 = False
    ENABLE_ATR_FILTER_2 = False
    ENABLE_VOLUME_FILTER = True
    ENABLE_RSI_EMA_FILTER = False
    ENABLE_EMA_FILTER = False
    ENABLE_ADX_FILTER = False
    ENABLE_RSI_FILTER = False
    ENABLE_BB_FILTER = False
    print("✅ Signal detection mode applied - Using relaxed thresholds")

def apply_conservative_strategy():
    """Conservative strategy with all filters enabled"""
    global ENABLE_ATR_FILTER_1, ENABLE_ATR_FILTER_2, ENABLE_VOLUME_FILTER
    global ENABLE_RSI_EMA_FILTER, ENABLE_EMA_FILTER, ENABLE_ADX_FILTER
    global ENABLE_RSI_FILTER, ENABLE_BB_FILTER, POSITION_SIZE_PCT
    
    ENABLE_ATR_FILTER_1 = True
    ENABLE_ATR_FILTER_2 = True
    ENABLE_VOLUME_FILTER = True
    ENABLE_RSI_EMA_FILTER = True
    ENABLE_EMA_FILTER = True
    ENABLE_ADX_FILTER = True
    ENABLE_RSI_FILTER = True
    ENABLE_BB_FILTER = True
    POSITION_SIZE_PCT = 25  # Lower risk
    print("✅ Conservative strategy applied")


def apply_aggressive_strategy():
    """Aggressive strategy with minimal filters"""
    global ENABLE_ATR_FILTER_1, ENABLE_ATR_FILTER_2, ENABLE_VOLUME_FILTER
    global ENABLE_RSI_EMA_FILTER, ENABLE_EMA_FILTER, ENABLE_ADX_FILTER
    global ENABLE_RSI_FILTER, ENABLE_BB_FILTER, POSITION_SIZE_PCT
    
    ENABLE_ATR_FILTER_1 = False
    ENABLE_ATR_FILTER_2 = False
    ENABLE_VOLUME_FILTER = False
    ENABLE_RSI_EMA_FILTER = False
    ENABLE_EMA_FILTER = False
    ENABLE_ADX_FILTER = False
    ENABLE_RSI_FILTER = False
    ENABLE_BB_FILTER = False
    POSITION_SIZE_PCT = 75  # Higher risk
    print("✅ Aggressive strategy applied")


def apply_balanced_strategy():
    """Balanced strategy with key filters"""
    global ENABLE_ATR_FILTER_1, ENABLE_ATR_FILTER_2, ENABLE_VOLUME_FILTER
    global ENABLE_RSI_EMA_FILTER, ENABLE_EMA_FILTER, ENABLE_ADX_FILTER
    global ENABLE_RSI_FILTER, ENABLE_BB_FILTER, POSITION_SIZE_PCT
    
    ENABLE_ATR_FILTER_1 = False
    ENABLE_ATR_FILTER_2 = True
    ENABLE_VOLUME_FILTER = True
    ENABLE_RSI_EMA_FILTER = True
    ENABLE_EMA_FILTER = True
    ENABLE_ADX_FILTER = False
    ENABLE_RSI_FILTER = False
    ENABLE_BB_FILTER = False
    POSITION_SIZE_PCT = 50  # Moderate risk
    print("✅ Balanced strategy applied")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
# To use a preset strategy in your code:
from strategy_variables import *
apply_conservative_strategy()

# Or modify individual variables:
from strategy_variables import *
ENABLE_EMA_FILTER = True
POSITION_SIZE_PCT = 30
BASIS_TYPE = "TEMA"
"""
