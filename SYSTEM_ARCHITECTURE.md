# 🏗️ AlphaForge Trading System - Complete Architecture Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Components](#core-components)
4. [Signal Generation Workflow](#signal-generation-workflow)
5. [Data Flow](#data-flow)
6. [Trading Strategy](#trading-strategy)
7. [Risk Management](#risk-management)
8. [Technology Stack](#technology-stack)
9. [API Endpoints](#api-endpoints)
10. [Database Schema](#database-schema)

---

## System Overview

**AlphaForge** is an automated forex/gold trading system that uses multi-indicator analysis and AI-powered validation to generate high-probability trading signals for GBP/USD, XAU/USD (Gold), and USD/JPY.

### Key Features
- ✅ **Multi-Timeframe Analysis**: M5, M15, H1 confluence
- ✅ **6-Indicator Voting System**: EMA Ribbon, RSI, MACD, Bollinger Bands, Stochastic, Volume
- ✅ **Market Regime Detection**: Trending, ranging, volatile, choppy
- ✅ **Kelly Criterion Position Sizing**: Optimal risk allocation
- ✅ **Gemini AI Validation**: 2-factor authentication for signals
- ✅ **Real-time OANDA Integration**: Live market data
- ✅ **Comprehensive Backtesting**: Historical performance analysis
- ✅ **Trading Journal**: Track and analyze all trades

### System Goals
1. Generate **2-3 high-quality signals per day** on M5 timeframe
2. Achieve **60-70% win rate** with strict filters (min_votes=3.0)
3. Maintain **2:1 risk/reward ratio** on every trade
4. Adapt position sizing based on market conditions
5. Provide full transparency with AI reasoning

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │ Signals  │  │ Journal  │  │Analytics │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                   API Layer                             │    │
│  │  /api/signals, /api/journal, /api/stats, /api/backtest │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ▲                                   │
│                              │                                   │
│  ┌──────────────────┬────────┴────────┬──────────────────┐    │
│  │                  │                 │                   │    │
│  ▼                  ▼                 ▼                   ▼    │
│ ┌──────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐  │
│ │Signal│  │Multi-Timeframe│  │ Regime   │  │   Kelly      │  │
│ │Gen.  │  │   Engine      │  │ Detector │  │ Criterion    │  │
│ └──────┘  └──────────────┘  └──────────┘  └──────────────┘  │
│                              │                                   │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  Gemini AI       │                         │
│                    │  Validator       │                         │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ OANDA API    │  │ PostgreSQL   │  │ Redis Cache  │         │
│  │(Live Prices) │  │  (Signals,   │  │ (Performance)│         │
│  │              │  │   Journal)   │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Multi-Timeframe Engine (`multi_timeframe_engine.py`)

**Purpose**: Core signal generation using 6-indicator voting system across 3 timeframes

**How It Works**:
```python
# 1. Fetch data from OANDA
M5_data  = fetch_candles(instrument, 'M5', 500 bars)   # 40% weight
M15_data = fetch_candles(instrument, 'M15', 300 bars)  # 35% weight
H1_data  = fetch_candles(instrument, 'H1', 200 bars)   # 25% weight

# 2. Calculate 6 technical indicators per timeframe
indicators = {
    'EMA_Ribbon': EMA(5, 8, 13),     # Trend direction
    'RSI': RSI(7),                    # Momentum
    'MACD': MACD(6, 13, 4),          # Trend strength
    'Bollinger': BB(20, 2.0),        # Volatility
    'Stochastic': Stoch(5, 3),       # Overbought/oversold
    'Volume': Volume analysis         # Confirmation
}

# 3. Each indicator votes BUY (1.0), SELL (-1.0), or NEUTRAL (0.0)
# 6 indicators × 3 timeframes = 18 possible votes

# 4. Calculate weighted average
buy_votes = (M5_buy × 0.40) + (M15_buy × 0.35) + (H1_buy × 0.25)
sell_votes = (M5_sell × 0.40) + (M15_sell × 0.35) + (H1_sell × 0.25)

# 5. Decision logic
if buy_votes >= min_votes_required (default: 2.5):
    signal = 'BUY'
elif sell_votes >= min_votes_required:
    signal = 'SELL'
else:
    signal = 'NEUTRAL'
```

**Indicator Logic**:

```python
# Example: EMA Ribbon Voting
def ema_ribbon_vote(close_prices):
    ema5 = EMA(close, 5)
    ema8 = EMA(close, 8)
    ema13 = EMA(close, 13)
    
    # Bullish: Fast EMA above slow EMA
    if ema5 > ema8 > ema13:
        return 1.0  # BUY vote
    # Bearish: Fast EMA below slow EMA
    elif ema5 < ema8 < ema13:
        return -1.0  # SELL vote
    else:
        return 0.0  # NEUTRAL

# Similar logic for all 6 indicators
```

**Quality Filters**:
```python
filters = {
    'volatility': 0.05% <= ATR/price <= 0.25%,  # Not too quiet, not too chaotic
    'strength': signal_strength >= 40%,          # Minimum conviction
    'adx': ADX >= 15,                            # Minimum trend strength
    'spread': spread <= 2 pips                   # Low transaction cost
}

# Signal only passes if ALL filters are met
if all(filters.values()):
    signal_approved = True
```

---

### 2. Regime Detector (`regime_detector.py`)

**Purpose**: Classify market conditions to adapt strategy behavior

**How It Works**:
```python
# 1. Extract market features (500 bars)
features = {
    'volatility': ATR / close_price,
    'trend_strength': ADX,
    'momentum': RSI deviation from 50,
    'range_bound': (high - low) / ATR
}

# 2. Gaussian Mixture Model (unsupervised ML)
from sklearn.mixture import GaussianMixture
gmm = GaussianMixture(n_components=4)  # 4 market regimes
regime = gmm.fit_predict(features)

# 3. Classify into 4 regimes
regimes = {
    0: 'TRENDING',    # Strong directional movement (ADX > 25, low volatility)
    1: 'RANGING',     # Sideways market (ADX < 20, medium volatility)
    2: 'VOLATILE',    # High uncertainty (ATR > 0.20%, erratic price)
    3: 'CHOPPY'       # No clear direction (whipsaws, false breakouts)
}

# 4. Decide if tradeable
tradeable_regimes = ['TRENDING', 'RANGING']
should_trade = (regime in tradeable_regimes)
```

**Regime Impact on Strategy**:
```python
if regime == 'TRENDING':
    min_votes_required = 2.5      # Easier to trade trends
    position_multiplier = 1.2     # Increase position size
    
elif regime == 'RANGING':
    min_votes_required = 2.5      # Mean reversion works
    position_multiplier = 1.0     # Standard size
    
elif regime == 'VOLATILE':
    min_votes_required = 3.0      # Require stronger signal
    position_multiplier = 0.7     # Reduce exposure
    
elif regime == 'CHOPPY':
    should_trade = False          # Skip trading entirely
```

---

### 3. Kelly Criterion (`kelly_criterion.py`)

**Purpose**: Calculate optimal position size based on historical win rate and risk/reward

**How It Works**:
```python
# 1. Track last 50 trades
trades = {
    'wins': 32,
    'losses': 18,
    'avg_win': $466,
    'avg_loss': $238
}

# 2. Calculate Kelly Fraction
win_rate = 32 / 50 = 0.64 (64%)
avg_rr_ratio = 466 / 238 = 1.96 (almost 2:1)

kelly_fraction = (win_rate * avg_rr_ratio - (1 - win_rate)) / avg_rr_ratio
               = (0.64 × 1.96 - 0.36) / 1.96
               = 0.456 (45.6%)

# 3. Apply safety multiplier (conservative)
kelly_multiplier = 0.25  # Use 25% of Kelly (safe)
recommended_risk = kelly_fraction × kelly_multiplier
                 = 0.456 × 0.25
                 = 0.114 (11.4% of account)

# 4. Cap at maximum risk
final_risk = min(recommended_risk, 0.02)  # Never exceed 2%
           = 0.02 (2% per trade)
```

**Dynamic Adjustment**:
```python
# Update after each trade
def update_trade_result(profit_loss, risk):
    if profit_loss > 0:
        wins += 1
        total_win_amount += profit_loss
    else:
        losses += 1
        total_loss_amount += abs(profit_loss)
    
    # Recalculate Kelly for next trade
    new_kelly = calculate_kelly_fraction()
```

---

### 4. Gemini AI Validator (`gemini/simple_validator.py`)

**Purpose**: Use Google Gemini AI as 2nd layer validation to filter out low-quality signals

**How It Works**:
```python
# 1. Prepare signal data for AI
signal_context = {
    'instrument': 'XAU_USD',
    'direction': 'BUY',
    'entry': 2651.42,
    'stop_loss': 2646.25,
    'take_profit': 2661.76,
    'timeframe_signals': {
        'M5': {'vote': 2.5, 'ema': 'bullish', 'rsi': 45, 'macd': 'positive'},
        'M15': {'vote': 2.0, 'ema': 'bullish', 'rsi': 48, 'macd': 'positive'},
        'H1': {'vote': 1.5, 'ema': 'neutral', 'rsi': 52, 'macd': 'weak'}
    },
    'market_regime': 'TRENDING',
    'filters': {
        'volatility': 'OK (0.11%)',
        'strength': 'OK (41.7%)',
        'adx': 'OK (25.6)',
        'spread': 'OK (1.2 pips)'
    }
}

# 2. Send to Gemini AI
prompt = f"""
You are a professional forex trader analyzing a trading signal.

Signal Details:
{json.dumps(signal_context, indent=2)}

Question: Should I take this {direction} trade on {instrument}?

Analyze:
1. Multi-timeframe agreement (M5, M15, H1)
2. Quality of indicator signals
3. Market regime suitability
4. Risk/reward ratio (1:{rr})
5. Any red flags or concerns

Provide:
- Decision: APPROVE or REJECT
- Confidence: 0-100%
- Reasoning: 2-3 sentences
"""

response = gemini_api.generate_content(prompt)

# 3. Parse AI response
ai_decision = {
    'decision': 'APPROVE',
    'confidence': 75.0,
    'reasoning': "Strong bullish alignment on M5 and M15 with trending regime. 
                  H1 is neutral but not bearish. 2:1 RR is favorable. 
                  Volatility and spread are optimal. Take the trade."
}

# 4. Final decision (both must agree)
if ai_decision['decision'] == 'APPROVE' and ai_decision['confidence'] >= 70:
    final_decision = 'TAKE_TRADE'
else:
    final_decision = 'SKIP_TRADE'
```

**AI Rejection Examples**:
```
❌ "Conflicting signals between M5 (bullish) and H1 (bearish). Wait for alignment."
❌ "Choppy regime detected. High probability of whipsaw. Skip."
❌ "Spread too wide (3.5 pips). Transaction cost eats into profit potential."
❌ "RSI overbought (85) on all timeframes. Potential reversal imminent."
```

---

### 5. Enhanced Signal Generator (`enhanced_signal_generator.py`)

**Purpose**: Orchestrate all components to generate final trading signal

**Complete Workflow**:
```python
async def generate_signal(instrument='GBP_USD'):
    # Step 1: Fetch multi-timeframe data (3 API calls in parallel)
    mtf_data = await mtf_engine.fetch_multi_timeframe(instrument)
    # Returns: {'M5': DataFrame, 'M15': DataFrame, 'H1': DataFrame}
    
    # Step 2: Detect market regime
    regime = regime_detector.detect_regime(mtf_data['M5'], instrument)
    # Returns: 'TRENDING', 'RANGING', 'VOLATILE', or 'CHOPPY'
    
    # Step 3: Check if regime is tradeable
    if not regime_detector.should_trade(regime):
        return {
            'signal': 'SKIP',
            'reason': f'Unfavorable regime: {regime}',
            'tradeable': False
        }
    
    # Step 4: Generate multi-timeframe signal with regime context
    mtf_signal = mtf_engine.generate_multi_timeframe_signal(
        mtf_data, 
        market_regime=regime
    )
    
    # Step 5: Check quality filters
    if not mtf_signal['passed_filters']:
        return {
            'signal': 'SKIP',
            'reason': 'Failed quality filters',
            'filter_results': mtf_signal['filter_results']
        }
    
    # Step 6: Calculate Kelly position sizing
    kelly_fraction = kelly_criterion.calculate_fraction(instrument)
    recommended_risk = kelly_fraction * 0.25  # 25% of Kelly
    
    # Step 7: Validate with Gemini AI
    ai_validation = await gemini_validator.validate_signal(mtf_signal)
    
    if ai_validation['decision'] != 'APPROVE':
        return {
            'signal': 'SKIP',
            'reason': 'AI rejected',
            'ai_reasoning': ai_validation['reasoning']
        }
    
    # Step 8: Calculate final signal
    signal = {
        'instrument': instrument,
        'symbol': instrument.replace('_', ''),
        'direction': mtf_signal['signal'],  # BUY or SELL
        'entry': mtf_signal['entry_price'],
        'stop_loss': mtf_signal['stop_loss'],
        'take_profit': mtf_signal['take_profit'],
        
        # Confidence metrics
        'confidence_score': (mtf_signal['strength'] + ai_validation['confidence']) / 2,
        'buy_votes': mtf_signal['buy_votes'],
        'sell_votes': mtf_signal['sell_votes'],
        'strength': mtf_signal['strength'],
        
        # Market context
        'market_regime': regime,
        'regime_tradeable': True,
        'session_weight': calculate_session_weight(),
        
        # Risk management
        'recommended_risk': min(recommended_risk, 0.02),  # Max 2%
        'kelly_fraction': kelly_fraction,
        'position_multiplier': get_regime_multiplier(regime),
        
        # Timeframe breakdown
        'mtf_m5': mtf_signal['timeframe_signals']['M5'],
        'mtf_m15': mtf_signal['timeframe_signals']['M15'],
        'mtf_h1': mtf_signal['timeframe_signals']['H1'],
        'agreement': calculate_timeframe_agreement(mtf_signal),
        
        # AI validation
        'ai_decision': ai_validation['decision'],
        'ai_confidence': ai_validation['confidence'],
        'reasoning': ai_validation['reasoning'],
        
        # Technical details
        'atr': mtf_signal['atr'],
        'volatility': mtf_signal['volatility'],
        'adx': mtf_signal['adx'],
        'spread': mtf_signal['spread'],
        
        'timestamp': datetime.now().isoformat(),
        'strategy_version': 'AlphaForge-Enhanced-v2.0'
    }
    
    return signal
```

---

## Signal Generation Workflow

### Complete Flow (Step-by-Step)

```
┌────────────────────────────────────────────────────────────┐
│  USER ACTION: Click "Generate Signal" for GBP/USD          │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 1: Fetch Multi-Timeframe Data from OANDA             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ M5:  500 bars (last 2.5 days)   - 40% weight       │  │
│  │ M15: 300 bars (last 3 days)     - 35% weight       │  │
│  │ H1:  200 bars (last 8 days)     - 25% weight       │  │
│  └─────────────────────────────────────────────────────┘  │
│  Time: ~1.2s (parallel fetch)                              │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 2: Calculate Technical Indicators (per timeframe)    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ • EMA Ribbon (5, 8, 13)                             │  │
│  │ • RSI (7)                                           │  │
│  │ • MACD (6, 13, 4)                                   │  │
│  │ • Bollinger Bands (20, 2.0)                         │  │
│  │ • Stochastic (5, 3)                                 │  │
│  │ • Volume Analysis                                   │  │
│  │ • ADX (14) - for filtering                          │  │
│  │ • ATR (14) - for SL/TP                              │  │
│  └─────────────────────────────────────────────────────┘  │
│  Time: ~0.3s                                               │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 3: Indicator Voting (each timeframe)                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ M5 Timeframe:                                       │  │
│  │   EMA Ribbon: +1.0 (bullish alignment)              │  │
│  │   RSI: +0.5 (45 - slightly bullish)                 │  │
│  │   MACD: +1.0 (positive histogram)                   │  │
│  │   Bollinger: +0.5 (near lower band)                 │  │
│  │   Stochastic: +1.0 (oversold, turning up)           │  │
│  │   Volume: +0.5 (increasing on up bars)              │  │
│  │   ─────────────────────────────────                 │  │
│  │   M5 Buy Votes: 4.5 / 6.0                           │  │
│  │                                                      │  │
│  │ M15 Timeframe: 3.5 / 6.0 buy votes                  │  │
│  │ H1 Timeframe: 2.0 / 6.0 buy votes                   │  │
│  └─────────────────────────────────────────────────────┘  │
│  Time: ~0.1s                                               │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 4: Weighted Average Calculation                      │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Buy Votes = (4.5 × 0.40) + (3.5 × 0.35) + (2.0 × 0.25) │
│  │           = 1.80 + 1.23 + 0.50                       │  │
│  │           = 3.53 votes                               │  │
│  │                                                      │  │
│  │ Sell Votes = 0.5 (minimal bearish signals)          │  │
│  │                                                      │  │
│  │ Decision: BUY (3.53 >= min_votes 2.5)                │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 5: Regime Detection (Gaussian Mixture Model)         │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Features Extracted:                                  │  │
│  │   Volatility: 0.11% (low-medium)                     │  │
│  │   ADX: 25.6 (trending)                               │  │
│  │   RSI Dev: 5.0 (bullish momentum)                    │  │
│  │   Range/ATR: 1.2 (normal)                            │  │
│  │                                                      │  │
│  │ GMM Classification: TRENDING ✅                      │  │
│  │ Tradeable: Yes                                       │  │
│  │ Position Multiplier: 1.2x                            │  │
│  └─────────────────────────────────────────────────────┘  │
│  Time: ~0.2s                                               │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 6: Quality Filters                                   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ ✅ Volatility: 0.11% (in range 0.05-0.25%)           │  │
│  │ ✅ Strength: 58.8% (>= 40%)                          │  │
│  │ ✅ ADX: 25.6 (>= 15 for trend)                       │  │
│  │ ✅ Spread: 1.2 pips (<= 2 pips)                      │  │
│  │                                                      │  │
│  │ All Filters Passed ✅                                │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 7: Calculate Entry, SL, TP                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Current Price: 1.2650                                │  │
│  │ ATR (M5): 0.00045                                    │  │
│  │                                                      │  │
│  │ Entry: 1.2650 (market price)                         │  │
│  │ Stop Loss: 1.2650 - (0.00045 × 1.5) = 1.26433       │  │
│  │ Take Profit: 1.2650 + (0.00045 × 3.0) = 1.26635     │  │
│  │                                                      │  │
│  │ SL Distance: 6.7 pips                                │  │
│  │ TP Distance: 13.5 pips                               │  │
│  │ Risk:Reward = 1:2.0 ✅                               │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 8: Kelly Criterion Position Sizing                   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Historical Stats (last 50 trades):                   │  │
│  │   Win Rate: 64%                                      │  │
│  │   Avg Win: $466                                      │  │
│  │   Avg Loss: $238                                     │  │
│  │   RR Ratio: 1.96:1                                   │  │
│  │                                                      │  │
│  │ Kelly Fraction: 45.6%                                │  │
│  │ Kelly × 0.25 (conservative): 11.4%                   │  │
│  │ Capped at Max: 2.0%                                  │  │
│  │                                                      │  │
│  │ Recommended Risk: 2.0% per trade ✅                  │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 9: Gemini AI Validation                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ AI Prompt:                                           │  │
│  │ "Should I take this BUY trade on GBP/USD?"           │  │
│  │                                                      │  │
│  │ Context Provided:                                    │  │
│  │ • All indicator votes                                │  │
│  │ • Multi-timeframe signals                            │  │
│  │ • Market regime                                      │  │
│  │ • Quality filter results                             │  │
│  │ • Risk/reward ratio                                  │  │
│  │                                                      │  │
│  │ AI Response:                                         │  │
│  │ Decision: APPROVE ✅                                 │  │
│  │ Confidence: 78%                                      │  │
│  │ Reasoning: "Strong bullish alignment across M5/M15   │  │
│  │ with trending regime. H1 neutral but not            │  │
│  │ contradictory. 2:1 RR favorable. Take trade."        │  │
│  └─────────────────────────────────────────────────────┘  │
│  Time: ~0.8s (API call)                                    │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 10: Final Signal Package                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ ✅ SIGNAL APPROVED                                   │  │
│  │                                                      │  │
│  │ Pair: GBP/USD                                        │  │
│  │ Direction: BUY                                       │  │
│  │ Entry: 1.2650                                        │  │
│  │ Stop Loss: 1.26433 (-6.7 pips)                       │  │
│  │ Take Profit: 1.26635 (+13.5 pips)                    │  │
│  │                                                      │  │
│  │ Confidence: 68.4% (avg of strength + AI)             │  │
│  │ Market Regime: TRENDING                              │  │
│  │ Recommended Risk: 2.0%                               │  │
│  │                                                      │  │
│  │ AI Reasoning: "Strong bullish alignment..."          │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 11: Save to Database & Display                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 1. Insert into TradingSignal table                   │  │
│  │ 2. Send to frontend via API response                 │  │
│  │ 3. Optional: Send Telegram notification              │  │
│  │ 4. Log to system for monitoring                      │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│  TOTAL TIME: ~2.5 seconds                                  │
│  DECISION: TAKE TRADE ✅                                   │
└────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Real-Time Trading Flow

```
1. USER INITIATES
   ↓
   [Frontend Button Click] → "Generate Signal for XAU/USD"
   
2. API REQUEST
   ↓
   POST /api/signals/enhanced/generate/XAU_USD
   
3. BACKEND PROCESSING
   ↓
   EnhancedSignalGenerator.generate_signal('XAU_USD')
   ├─→ Fetch M5, M15, H1 data from OANDA (parallel)
   ├─→ Calculate 6 indicators per timeframe
   ├─→ Vote aggregation (weighted)
   ├─→ Regime detection (GMM)
   ├─→ Quality filters
   ├─→ Calculate SL/TP (ATR-based)
   ├─→ Kelly position sizing
   └─→ Gemini AI validation
   
4. DECISION
   ↓
   if APPROVED:
      └─→ Save to database (TradingSignal table)
      └─→ Return signal to frontend
      └─→ Display in dashboard
   else:
      └─→ Return rejection reason
      └─→ Log for analysis
      
5. USER EXECUTES (Manual or Auto)
   ↓
   [User enters trade on broker platform]
   └─→ Update signal status: PENDING → ACTIVE
   
6. TRADE MANAGEMENT
   ↓
   [Monitor position]
   └─→ Hit TP or SL
   └─→ Update signal: ACTIVE → CLOSED
   └─→ Record outcome (WIN/LOSS)
   └─→ Update Kelly Criterion stats
   
7. JOURNAL ENTRY
   ↓
   [User adds trade to journal]
   └─→ Record actual entry/exit prices
   └─→ Calculate actual P&L
   └─→ Add notes/screenshots
   └─→ Update statistics
```

---

## Trading Strategy

### Multi-Indicator Voting Strategy

**Core Principle**: Multiple indicators must agree before taking a trade

#### Indicator Details

**1. EMA Ribbon (5, 8, 13)**
- **Purpose**: Trend direction
- **Bullish**: EMA5 > EMA8 > EMA13 (proper alignment)
- **Bearish**: EMA5 < EMA8 < EMA13 (inverse alignment)
- **Vote Weight**: 1.0 (strong directional signal)

**2. RSI (7)**
- **Purpose**: Momentum and overbought/oversold
- **Bullish**: RSI < 50 and rising (oversold recovery)
- **Bearish**: RSI > 50 and falling (overbought decline)
- **Vote Weight**: 0.5-1.0 (varies with extremity)

**3. MACD (6, 13, 4)**
- **Purpose**: Trend strength and momentum
- **Bullish**: MACD line > signal line, positive histogram
- **Bearish**: MACD line < signal line, negative histogram
- **Vote Weight**: 1.0 (strong momentum confirmation)

**4. Bollinger Bands (20, 2.0)**
- **Purpose**: Volatility and mean reversion
- **Bullish**: Price near lower band (oversold)
- **Bearish**: Price near upper band (overbought)
- **Vote Weight**: 0.5 (context-dependent)

**5. Stochastic (5, 3)**
- **Purpose**: Overbought/oversold conditions
- **Bullish**: %K and %D < 20 and crossing up
- **Bearish**: %K and %D > 80 and crossing down
- **Vote Weight**: 1.0 (strong reversal signal)

**6. Volume Analysis**
- **Purpose**: Confirm price action
- **Bullish**: Increasing volume on up bars
- **Bearish**: Increasing volume on down bars
- **Vote Weight**: 0.5 (confirmation only)

### Signal Strength Calculation

```python
# Maximum possible votes per timeframe: 6.0
# Across 3 timeframes with weights:

max_votes = (6.0 × 0.40) + (6.0 × 0.35) + (6.0 × 0.25)
          = 2.4 + 2.1 + 1.5
          = 6.0 total maximum

# Signal strength percentage
strength = (actual_votes / max_votes) × 100

# Example with 3.53 buy votes:
strength = (3.53 / 6.0) × 100 = 58.8%
```

---

## Risk Management

### Position Sizing Formula

```python
# 1. Calculate risk amount
account_balance = $10,000
risk_per_trade = 2.0%  # From Kelly Criterion (capped)
risk_amount = $10,000 × 0.02 = $200

# 2. Calculate SL distance
entry_price = 1.2650
stop_loss = 1.26433
sl_distance = |1.2650 - 1.26433| = 0.00067 (6.7 pips)

# 3. Calculate position size
position_size = risk_amount / sl_distance
              = $200 / 0.00067
              = 298,507 units (2.99 standard lots)

# 4. Verify lot size
# 1 standard lot = 100,000 units
# Position = 2.99 lots ≈ 3 mini lots (30,000 units each)
```

### Stop Loss & Take Profit Logic

```python
# ATR-based dynamic SL/TP
def calculate_sl_tp(entry_price, direction, atr):
    """
    SL: 1.5× ATR from entry (allows breathing room)
    TP: 3.0× ATR from entry (2:1 risk/reward)
    """
    if direction == 'BUY':
        stop_loss = entry_price - (atr × 1.5)
        take_profit = entry_price + (atr × 3.0)
    else:  # SELL
        stop_loss = entry_price + (atr × 1.5)
        take_profit = entry_price - (atr × 3.0)
    
    return stop_loss, take_profit

# Example for Gold (XAU/USD)
entry = 2651.42
atr = 4.83  # Gold ATR typically $3-5

sl = 2651.42 - (4.83 × 1.5) = 2644.17 ($7.25 below)
tp = 2651.42 + (4.83 × 3.0) = 2665.91 ($14.49 above)

# Risk: $7.25 per lot
# Reward: $14.49 per lot
# R/R: 1:2.0 ✅
```

### Why 2:1 Risk/Reward Works

```
With 2:1 R/R, you only need 33.3% win rate to break even:

Scenario: 100 trades, 35% win rate
Wins: 35 trades × $200 profit = $7,000
Losses: 65 trades × $100 loss = $6,500
Net Profit: $7,000 - $6,500 = +$500

AlphaForge targets 60-70% win rate (strict filters)
With 60% WR and 2:1 R/R:
Wins: 60 × $200 = $12,000
Losses: 40 × $100 = $4,000
Net Profit: $8,000 (+80% ROI on risked capital)
```

---

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (async API)
- **Database**: PostgreSQL / SQLite
- **ORM**: SQLAlchemy 2.0
- **Async**: asyncio, aiohttp
- **Caching**: Redis + LRU cache
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 18
- **State Management**: React Hooks (useState, useEffect)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Charts**: Recharts / TradingView Widget
- **Routing**: React Router

### External APIs
- **OANDA API**: Real-time forex/gold prices, historical data
- **Google Gemini AI**: Signal validation and reasoning
- **Telegram Bot API**: Notifications (optional)

### DevOps
- **Version Control**: Git / GitHub
- **Package Manager**: pip, npm
- **Process Manager**: PM2, systemd
- **Reverse Proxy**: Nginx (production)
- **SSL**: Let's Encrypt

### Data Processing
- **pandas**: DataFrame manipulation
- **numpy**: Numerical computations
- **scikit-learn**: Machine learning (GMM for regime detection)
- **ta-lib / pandas-ta**: Technical indicators

---

## API Endpoints

### Signal Generation
```
POST /api/signals/enhanced/generate
→ Generate signals for all 3 pairs (GBP/USD, XAU/USD, USD/JPY)

POST /api/signals/enhanced/generate/{pair}
→ Generate signal for specific pair

GET /api/signals
→ Get all signals (paginated)

GET /api/signals/active
→ Get active trades

GET /api/signals/pending
→ Get pending signals (not entered yet)

GET /api/signals/{signal_id}
→ Get specific signal details

PUT /api/signals/{signal_id}/status
→ Update signal status (PENDING → ACTIVE → CLOSED)
```

### Trading Journal
```
POST /api/journal/entries
→ Create journal entry (record executed trade)

GET /api/journal/entries
→ Get all journal entries

GET /api/journal/entries/{entry_id}
→ Get specific entry

PUT /api/journal/entries/{entry_id}
→ Update journal entry

DELETE /api/journal/entries/{entry_id}
→ Delete journal entry

GET /api/journal/statistics
→ Get trading performance stats (win rate, P&L, etc.)
```

### Analytics & Statistics
```
GET /api/stats
→ Dashboard statistics (trades, win rate, profit)

GET /api/signals/statistics
→ Signal generation statistics

GET /api/signals/performance
→ Performance by symbol

GET /api/enhanced/statistics
→ Enhanced strategy statistics (Kelly, regime, etc.)
```

### Backtesting
```
Run via CLI: python backtest_oanda.py
Config: backtest_config.json
Results: JSON file with trade history
```

### System Status
```
GET /health
→ Health check

GET /api/status
→ System status (OANDA, Gemini, Database connectivity)

GET /api/metrics
→ Performance metrics (response times, cache hit rate)
```

---

## Database Schema

### TradingSignal Table
```sql
CREATE TABLE trading_signals (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Signal identification
    timestamp TIMESTAMP NOT NULL,
    pair VARCHAR(10) NOT NULL,              -- GBP_USD, XAU_USD, USD_JPY
    symbol VARCHAR(10),                     -- GBPUSD, XAUUSD, USDJPY
    direction VARCHAR(4) NOT NULL,          -- BUY or SELL
    
    -- Price levels
    entry_price FLOAT NOT NULL,
    stop_loss FLOAT NOT NULL,
    take_profit FLOAT NOT NULL,
    tp2 FLOAT,
    tp3 FLOAT,
    
    -- Trade execution
    status VARCHAR(20) DEFAULT 'PENDING',   -- PENDING, ACTIVE, CLOSED, CANCELLED
    outcome VARCHAR(20),                    -- WIN, LOSS, BREAKEVEN, NONE
    actual_entry FLOAT,
    actual_exit FLOAT,
    
    -- Performance
    pips_gained FLOAT,
    actual_pnl FLOAT,
    risk_reward_ratio VARCHAR(10),
    
    -- Signal quality
    confidence_score FLOAT,
    session_weight FLOAT,
    atr FLOAT,
    
    -- Enhanced metadata (JSON)
    metadata JSONB,                         -- Regime, MTF signals, Kelly, etc.
    reasoning TEXT,                         -- AI reasoning
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_pair_status_timestamp (pair, status, timestamp),
    INDEX idx_status_confidence (status, confidence_score),
    INDEX idx_pair_outcome_timestamp (pair, outcome, timestamp)
);
```

### JournalEntry Table
```sql
CREATE TABLE journal_entries (
    id SERIAL PRIMARY KEY,
    
    -- Trade details
    date DATE NOT NULL,
    pair VARCHAR(10) NOT NULL,
    direction VARCHAR(4) NOT NULL,
    entry_price FLOAT NOT NULL,
    exit_price FLOAT NOT NULL,
    stop_loss FLOAT,
    take_profit FLOAT,
    
    -- Performance
    pips FLOAT,
    profit_loss FLOAT,
    r_multiple FLOAT,                       -- R (risk units)
    
    -- Context
    setup VARCHAR(50),
    timeframe VARCHAR(10),
    notes TEXT,
    screenshot_url VARCHAR(255),
    tags JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_date (date),
    INDEX idx_pair (pair)
);
```

---

## Configuration Files

### backtest_config.json
```json
{
  "backtest_config": {
    "instrument": "XAU_USD",
    "start_date": "2024-10-01",
    "end_date": "2024-10-31",
    "initial_balance": 10000,
    "risk_per_trade": 0.02,
    "granularity": "M5",
    "min_votes_required": 1.5,
    "min_strength": 30.0,
    "focus_date": null
  }
}
```

### .env (Environment Variables)
```env
# OANDA API
OANDA_API_KEY=your_oanda_api_key
OANDA_ACCOUNT_ID=your_account_id
OANDA_ENVIRONMENT=practice

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/alphaforge
DB_POOL_SIZE=20

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# Performance
ENABLE_COMPRESSION=true
RATE_LIMIT_PER_MINUTE=60
```

---

## How Different Components Work Together

### Example: Full Trade Lifecycle

```
DAY 1: 10:00 AM - Signal Generation
├─→ User clicks "Generate Signal" for XAU/USD
├─→ System fetches M5, M15, H1 data from OANDA
├─→ 6 indicators vote across 3 timeframes
├─→ Weighted vote: 3.8 BUY votes (strong)
├─→ Regime: TRENDING (favorable)
├─→ Filters: ALL PASS ✅
├─→ Kelly: 2% risk recommended
├─→ Gemini AI: APPROVE (82% confidence)
├─→ Signal saved to database (status: PENDING)
└─→ Display on dashboard with reasoning

DAY 1: 10:05 AM - User Enters Trade
├─→ User reviews signal on OANDA platform
├─→ Entry: $2651.42
├─→ SL: $2644.17 (-$7.25, 1.5× ATR)
├─→ TP: $2665.91 (+$14.49, 3.0× ATR)
├─→ Position: 2.5 lots ($200 risk / $7.25 = 27.5 units)
├─→ User updates signal status: PENDING → ACTIVE
└─→ System records actual_entry_price: $2651.50

DAY 1: 2:30 PM - Take Profit Hit
├─→ Price reaches $2665.91
├─→ Trade closed automatically by broker
├─→ User updates signal: ACTIVE → CLOSED
├─→ Outcome: WIN
├─→ Actual P&L: $2665.91 - $2651.50 = $14.41 × 27.5 = $396
├─→ Pips: 145 pips
└─→ System updates Kelly Criterion (add 1 win)

DAY 1: 2:35 PM - Journal Entry
├─→ User creates journal entry
├─→ Records actual prices, P&L, R-multiple (2.0R)
├─→ Adds screenshot of trade
├─→ Notes: "Perfect trending setup, followed plan"
├─→ Tags: ["gold", "trending", "london-session"]
└─→ Statistics updated: Win rate 65% → 66%

DAY 2: 10:00 AM - Next Signal
├─→ System generates new signal
├─→ Kelly Criterion now uses updated 66% win rate
├─→ Recommended risk: 2.1% (Kelly increased)
├─→ Position size adjusted accordingly
└─→ Cycle repeats...
```

---

## Performance Characteristics

### Signal Generation Speed
- **Data Fetching**: 0.8-1.2s (parallel OANDA API calls)
- **Indicator Calculation**: 0.2-0.3s
- **Regime Detection**: 0.1-0.2s
- **Gemini AI Validation**: 0.5-1.0s
- **Total**: 1.8-2.7 seconds per signal

### Accuracy Metrics
- **Win Rate** (strict filters, min_votes=3.0): 60-70%
- **Win Rate** (relaxed filters, min_votes=1.5): 38-45%
- **Profit Factor** (strict): 2.0-2.5
- **Profit Factor** (relaxed): 1.2-1.5
- **Average R-multiple**: 1.8-2.2

### Signal Frequency
- **Strict Filters** (min_votes=3.0, strength=50%): 0-5 signals/month per pair
- **Moderate Filters** (min_votes=2.5, strength=40%): 15-25 signals/month per pair
- **Relaxed Filters** (min_votes=1.5, strength=30%): 100-200 signals/month per pair

---

## Summary

**AlphaForge** is a sophisticated multi-layer trading system that:

1. **Collects** real-time market data from OANDA across 3 timeframes
2. **Analyzes** using 6 technical indicators with weighted voting
3. **Detects** market regime using machine learning (GMM)
4. **Filters** signals through quality checks (volatility, strength, ADX, spread)
5. **Calculates** optimal position size using Kelly Criterion
6. **Validates** with Gemini AI for final approval
7. **Manages** risk with ATR-based dynamic SL/TP (2:1 ratio)
8. **Tracks** all trades in database and journal
9. **Backtests** on historical data to verify strategy performance
10. **Adapts** continuously based on real trade outcomes

The system is designed to be **conservative** (multiple layers of confirmation), **adaptive** (Kelly sizing, regime detection), and **transparent** (AI reasoning, full audit trail).

---

**Key Principle**: *"Trade only when multiple indicators across multiple timeframes agree, in favorable market conditions, with AI confirmation, and optimal position sizing."*

This multi-layer approach reduces false signals and increases probability of success, making it suitable for serious traders who value quality over quantity.

