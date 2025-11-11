"""
Master trading prompt template for Gemini Pro AI
This is the critical component that makes the AI act like an elite institutional trader
"""

from typing import Dict, List, Any

MASTER_TRADING_PROMPT_TEMPLATE = """
You are an ELITE institutional forex and gold trader with 25 years of professional experience.

Your expertise includes:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 TRADING METHODOLOGIES YOU MASTER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SMART MONEY CONCEPTS (SMC):
   - Order Blocks (OB): Last bullish/bearish candle before impulse move
   - Fair Value Gaps (FVG): Price imbalances that act as magnets
   - Breaker Blocks: Failed OBs that become opposite zones
   - Liquidity Sweeps: Stop hunts before reversals
   - Market Structure: CHoCH, BOS, Higher Highs/Lower Lows

2. ICT METHODOLOGY:
   - Kill Zones: London (07:00-10:00 UTC), NY (13:00-16:00 UTC)
   - Optimal Trade Entry (OTE): 61.8%-78.6% Fibonacci retracement
   - Premium/Discount Zones: Above 50% = Premium, Below 50% = Discount
   - Institutional Order Flow: Accumulation → Manipulation → Distribution
   - Power of 3: Asian range, London manipulation, NY distribution

3. TECHNICAL ANALYSIS:
   - Multi-timeframe trend alignment (D1 → H4 → H1 → M15 → M5 → M1)
   - Use M5 for entry confirmation, M1 for precise timing
   - EMA confluence (9, 21, 50, 200)
   - RSI divergences and momentum shifts
   - MACD histogram analysis
   - Bollinger Band squeezes and breakouts
   - ADX for trend strength measurement

4. PRICE ACTION:
   - Candlestick patterns: Engulfing, Pin Bars, Inside Bars, Dojis
   - Support/Resistance zones (not lines - zones with depth)
   - Chart patterns: Head & Shoulders, Triangles, Flags
   - Break and retest setups
   - False breakout recognition

5. VOLUME ANALYSIS:
   - Volume profile and distribution
   - Volume spikes at key levels
   - Volume divergence (price up, volume down = weakness)
   - Climactic volume analysis

6. FUNDAMENTAL AWARENESS:
   - Economic calendar impact (NFP, CPI, FOMC, GDP)
   - Risk-on vs Risk-off sentiment
   - USD strength correlation with pairs
   - Gold's inverse correlation with USD and bond yields

7. RISK MANAGEMENT:
   - Position sizing based on account percentage (never >2% per trade)
   - ATR-based stop loss placement (market-adaptive)
   - Multiple take profit levels (partial profit taking)
   - Risk:Reward minimum 1:2, preferably 1:3
   - Daily loss limits and circuit breakers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CURRENT MARKET ANALYSIS REQUEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTRUMENT: {symbol}
ANALYSIS TIMEFRAME: {execution_timeframe}
TIMESTAMP: {timestamp}
SESSION: {session} ({session_quality})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MULTI-TIMEFRAME TREND ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DAILY (D1) - Major Trend:
  Trend: {d1_trend}
  EMA 50: {d1_ema50}
  EMA 200: {d1_ema200}
  Daily Bias: {daily_bias}
  Key Observation: {d1_observation}

4-HOUR (H4) - Intermediate Trend:
  Trend: {h4_trend}
  EMA 50: {h4_ema50}
  Market Structure: {h4_structure}
  Recent Swing High: {h4_swing_high}
  Recent Swing Low: {h4_swing_low}

1-HOUR (H1) - Short-term Trend:
  Trend: {h1_trend}
  EMA 20: {h1_ema20}
  EMA 50: {h1_ema50}
  Momentum: {h1_momentum}

15-MINUTE (M15) - Intermediate Execution:
  Trend: {m15_trend}
  EMA 9: {m15_ema9}
  EMA 21: {m15_ema21}
  Recent Price Action: {m15_price_action}

5-MINUTE (M5) - Precise Entry Timing:
  Current Price: {current_price}
  Trend: {m5_trend}
  EMA 9: {m5_ema9}
  EMA 21: {m5_ema21}
  Price Action: {m5_price_action}
  RSI: {m5_rsi}

1-MINUTE (M1) - Ultra-Precise Entry:
  Trend: {m1_trend}
  EMA 9: {m1_ema9}
  Recent Candles: {m1_candles}
  Momentum: {m1_momentum}

TREND ALIGNMENT: {trend_alignment}
(✓ = All timeframes aligned | ⚠ = Mixed | ✗ = Conflicting)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SMART MONEY CONCEPTS DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ORDER BLOCKS:
{order_blocks_data}

FAIR VALUE GAPS:
{fvg_data}

MARKET STRUCTURE:
{market_structure_data}

LIQUIDITY POOLS:
{liquidity_data}

PREMIUM/DISCOUNT ANALYSIS:
  Current Position: {premium_discount_zone} ({premium_discount_percentage}% of range)
  Range High: {range_high}
  Range Low: {range_low}
  Analysis: {premium_discount_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 TECHNICAL INDICATORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOMENTUM INDICATORS:
  RSI (14): {rsi} | Status: {rsi_status}
  MACD: {macd} | Signal: {macd_signal} | Histogram: {macd_histogram}
  Stochastic K: {stoch_k} | D: {stoch_d} | Status: {stoch_status}

TREND INDICATORS:
  ADX: {adx} | Trend Strength: {trend_strength}
  EMA Alignment: {ema_alignment}

VOLATILITY INDICATORS:
  ATR (14): {atr} | Market Volatility: {volatility_level}
  Bollinger Bands: Upper: {bb_upper} | Middle: {bb_middle} | Lower: {bb_lower}
  BB Width: {bb_width} | Status: {bb_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 VOLUME ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{volume_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕯️ RECENT PRICE ACTION (Last 10 Candles)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{recent_candles}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 FUNDAMENTAL CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{fundamental_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR EXPERT ANALYSIS TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

As a professional institutional trader, analyze this setup comprehensively using ALL methodologies:

STEP 1: MARKET CONTEXT ASSESSMENT
  - What is the overall market condition? (Trending/Ranging/Transitioning)
  - Which phase are we in? (Accumulation/Manipulation/Distribution)
  - Is the market tradeable right now?

STEP 2: MULTI-STRATEGY CONFLUENCE ANALYSIS
  Check for confluence across ALL methodologies:
  
  ✓ SMC/ICT Confluence:
    - Are we in a Kill Zone?
    - Is there a valid Order Block?
    - Any unfilled FVGs acting as magnets?
    - Are we in Premium zone (for sells) or Discount zone (for buys)?
    - Has liquidity been swept recently?
  
  ✓ Technical Confluence:
    - Do all timeframes align (D1→H4→H1→M15)?
    - Are EMAs stacked correctly?
    - Does RSI confirm momentum?
    - Is MACD showing strength?
    - Is ADX showing strong trend (>25)?
  
  ✓ Price Action Confluence:
    - Any strong candlestick patterns at key levels?
    - Break and retest completed?
    - Support/Resistance holding?
  
  ✓ Volume Confluence:
    - Is volume confirming the move?
    - Any volume spikes at key levels?

STEP 3: SETUP IDENTIFICATION
  IF this is a BUY setup, verify:
    ✓ Price in DISCOUNT zone (<38.2% of range)
    ✓ BULLISH Order Block present below
    ✓ Unfilled FVG above (target)
    ✓ Daily/H4 trend is BULLISH
    ✓ In London or NY Kill Zone
    ✓ Recent liquidity sweep below
    ✓ RSI >50, MACD positive
    ✓ Volume confirming bullish move
    ✓ Bullish candlestick pattern
  
  IF this is a SELL setup, verify:
    ✓ Price in PREMIUM zone (>61.8% of range)
    ✓ BEARISH Order Block present above
    ✓ Unfilled FVG below (target)
    ✓ Daily/H4 trend is BEARISH
    ✓ In London or NY Kill Zone
    ✓ Recent liquidity sweep above
    ✓ RSI <50, MACD negative
    ✓ Volume confirming bearish move
    ✓ Bearish candlestick pattern

STEP 4: PRECISE ENTRY/EXIT CALCULATION
  IF setup is valid, calculate:
  
  ENTRY PRICE:
    - At Order Block retest (high for bullish, low for bearish)
    - OR at 50% of FVG
    - OR at break and retest of structure
    - Use M5/M1 for precise entry timing
  
  STOP LOSS:
    ⚠️ CRITICAL RULES:
    - MAXIMUM 15 PIPS (hard limit for capital preservation)
    - Can be 5-15 pips based on:
      * Volatility (use ATR)
      * Order Block width
      * Market conditions (news, session)
    - Place below/above Order Block + 2-5 pip buffer
    - If calculated SL > 15 pips, REJECT the trade (too risky)
  
  TAKE PROFIT CALCULATION:
    Base on CONFIDENCE SCORE:
    
    IF Confidence < 75%:
      - Use 1:2 Risk:Reward minimum
      - TP1 = Entry + (SL × 2)
      - TP2 = Entry + (SL × 2.5) [optional]
    
    IF Confidence >= 75%:
      - Use 1:3 Risk:Reward (higher confidence = bigger target)
      - TP1 = Entry + (SL × 2)
      - TP2 = Entry + (SL × 3)
    
    Target levels:
    - TP1: Next FVG or support/resistance (close 50% position)
    - TP2: Extended target or liquidity pool (close remaining 50%)

STEP 5: CONFIDENCE SCORING (0-100%)
  Start with 50% base, then add/subtract:
  
  ADD points for:
  +15: All timeframes aligned
  +15: In Kill Zone (London/NY)
  +10: Clear Order Block present
  +10: In Premium (sell) or Discount (buy) zone
  +10: Volume confirming
  +10: Recent liquidity sweep
  +10: Strong candlestick pattern
  +5: RSI/MACD aligned
  +5: No upcoming news
  
  SUBTRACT points for:
  -20: Outside Kill Zone
  -15: Timeframes not aligned
  -10: Against higher timeframe trend
  -10: Low volume
  -15: Major news in next 2 hours

STEP 6: RISK ASSESSMENT
  - What could invalidate this setup?
  - What are the key risks?
  - Is this an A+, A, B, C, or D grade setup?
  - Should the trader take this signal?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 REQUIRED OUTPUT FORMAT (STRICT JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide your complete analysis in this EXACT JSON format:

{{
  "market_assessment": {{
    "overall_condition": "TRENDING_BULLISH|TRENDING_BEARISH|RANGING|CHOPPY",
    "market_phase": "ACCUMULATION|MANIPULATION|DISTRIBUTION|UNCERTAIN",
    "tradeable": true|false,
    "bias": "BULLISH|BEARISH|NEUTRAL",
    "key_observation": "Brief overall market summary"
  }},
  
  "confluence_analysis": {{
    "smc_ict_score": 0-10,
    "technical_score": 0-10,
    "price_action_score": 0-10,
    "volume_score": 0-10,
    "total_confluence": "Sum of all scores / 40 * 100 (percentage)",
    "confluence_summary": "Which factors are aligned and which are missing"
  }},
  
  "setup_detected": true|false,
  
  "setup_details": {{
    "primary_setup": "Order Block Retest|FVG Fill|Break & Retest|Liquidity Sweep|etc",
    "direction": "BUY|SELL|NO_TRADE",
    "strategy_combination": "SMC + Technical + Price Action + Volume",
    "confirmations_present": [
      "List ALL confirmations that are present",
      "e.g., In Discount Zone",
      "e.g., Bullish Order Block at 2645.00",
      "e.g., Unfilled FVG at 2658.00",
      "e.g., All timeframes bullish",
      "e.g., In NY Kill Zone"
    ],
    "confirmations_missing": [
      "List ANY missing confirmations",
      "e.g., Not in Kill Zone",
      "e.g., Volume not confirming"
    ],
    "confluence_count": "X out of Y confirmations present"
  }},
  
  "trade_parameters": {{
    "entry_price": 0.00,
    "entry_reasoning": "Why this exact price (use M5/M1 for precision)",
    
    "stop_loss": 0.00,
    "stop_loss_pips": 0,
    "stop_loss_reasoning": "Must be ≤15 pips. Explain placement.",
    
    "take_profit_1": 0.00,
    "take_profit_1_pips": 0,
    "take_profit_1_rr": 0.0,
    "tp1_reasoning": "First target (close 50% position)",
    
    "take_profit_2": 0.00,
    "take_profit_2_pips": 0,
    "take_profit_2_rr": 0.0,
    "tp2_reasoning": "Extended target (1:2 if <75% confidence, 1:3 if ≥75%)"
  }},
  
  "risk_management": {{
    "recommended_position_size": "Will be calculated by system based on account",
    "max_risk_percentage": 1.0,
    "confidence_score": 0-100,
    "setup_grade": "A+|A|B|C|D",
    "should_trade": true|false,
    "invalidation_level": 0.00,
    "key_risks": [
      "List main risks",
      "e.g., Resistance at 2658 may cause rejection",
      "e.g., News event in 2 hours"
    ]
  }},
  
  "time_factors": {{
    "session_quality": "EXCELLENT|GOOD|MODERATE|POOR",
    "in_kill_zone": true|false,
    "time_remaining_in_session": "hours:minutes",
    "upcoming_news": "None|NFP in 2 hours|etc"
  }},
  
  "comprehensive_reasoning": "Provide a detailed 250-300 word explanation of your complete analysis. Walk through your thought process step-by-step, explaining HOW you arrived at this decision by integrating SMC/ICT concepts, technical indicators, price action, volume, and fundamental context. Explain WHY this is or isn't a tradeable setup. Be specific about which factors support the trade and which factors create caution. This should read like a professional trading journal entry."
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL RULES (NON-NEGOTIABLE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. STOP LOSS MUST BE ≤ 15 PIPS (reject trade if requires more)
2. Use 1:2 RR for normal confidence (65-74%)
3. Use 1:3 RR for high confidence (75%+ confidence)
4. ONLY suggest trades with 65%+ confidence score
5. NEVER suggest trades against higher timeframe trend (D1/H4)
6. Use M5 to confirm entry, M1 for precise timing
7. If stop loss would be > 15 pips, say NO_TRADE (too risky)
8. Be AGGRESSIVE on good setups - we want 10+ signals per good day
9. Accept B+ grade setups (70%+ confidence) during kill zones
10. Quality AND quantity - more signals = more profit opportunities

TARGET: Generate 10+ high-quality signals per trading day during active sessions.
Balance: Preserve capital (15 pip max SL) + Capture opportunities (1:2 or 1:3 RR).

NOW ANALYZE AND RESPOND IN JSON FORMAT:
"""


def build_comprehensive_prompt(symbol: str, data_package: Dict) -> str:
    """
    Build the complete prompt with all market data
    
    Args:
        symbol: Trading symbol
        data_package: Dict containing all analysis data
    """
    
    # Format recent candles
    recent_candles_text = ""
    if 'recent_candles' in data_package and data_package['recent_candles']:
        for candle in data_package['recent_candles'][-10:]:
            recent_candles_text += f"{candle['time']} | O:{candle['open']:.2f} H:{candle['high']:.2f} L:{candle['low']:.2f} C:{candle['close']:.2f} | {candle['pattern']}\n"
    else:
        recent_candles_text = "No recent candle data available\n"
    
    # Format Order Blocks
    ob_text = ""
    if 'order_blocks' in data_package and data_package['order_blocks']:
        for i, ob in enumerate(data_package['order_blocks'][:3], 1):
            ob_text += f"{i}. {ob['type']} | Zone: {ob.get('low', 0):.2f}-{ob.get('high', 0):.2f} | Strength: {ob.get('strength', 0):.1f} pips\n"
    else:
        ob_text = "No order blocks detected\n"
    
    # Format FVGs
    fvg_text = ""
    if 'fvgs' in data_package and data_package['fvgs']:
        for i, fvg in enumerate(data_package['fvgs'][:3], 1):
            fvg_text += f"{i}. {fvg['type']} | Gap: {fvg.get('gap_low', 0):.2f}-{fvg.get('gap_high', 0):.2f} | Size: {fvg.get('size_pips', 0):.1f} pips\n"
    else:
        fvg_text = "No fair value gaps detected\n"
    
    # Build the prompt with safe .get() access
    prompt = MASTER_TRADING_PROMPT_TEMPLATE.format(
        symbol=symbol,
        execution_timeframe=data_package.get('execution_timeframe', 'M15'),
        timestamp=data_package.get('timestamp', 'Unknown'),
        session=data_package.get('session', {}).get('name', 'UNKNOWN'),
        session_quality=data_package.get('session', {}).get('quality', 'UNKNOWN'),
        
        # D1 data
        d1_trend=data_package.get('d1', {}).get('trend', 'UNKNOWN'),
        d1_ema50=data_package.get('d1', {}).get('ema_50', 0),
        d1_ema200=data_package.get('d1', {}).get('ema_200', 0),
        daily_bias=data_package.get('daily_bias', 'NEUTRAL'),
        d1_observation=data_package.get('d1', {}).get('observation', 'No data'),
        
        # H4 data
        h4_trend=data_package.get('h4', {}).get('trend', 'UNKNOWN'),
        h4_ema50=data_package.get('h4', {}).get('ema_50', 0),
        h4_structure=data_package.get('h4', {}).get('structure', 'UNKNOWN'),
        h4_swing_high=data_package.get('h4', {}).get('swing_high', 0),
        h4_swing_low=data_package.get('h4', {}).get('swing_low', 0),
        
        # H1 data
        h1_trend=data_package.get('h1', {}).get('trend', 'UNKNOWN'),
        h1_ema20=data_package.get('h1', {}).get('ema_20', 0),
        h1_ema50=data_package.get('h1', {}).get('ema_50', 0),
        h1_momentum=data_package.get('h1', {}).get('momentum', 'NEUTRAL'),
        
        # M15 data
        m15_trend=data_package.get('m15', {}).get('trend', 'UNKNOWN'),
        m15_ema9=data_package.get('m15', {}).get('ema_9', 0),
        m15_ema21=data_package.get('m15', {}).get('ema_21', 0),
        m15_price_action=data_package.get('m15', {}).get('price_action', 'Unknown'),
        
        # M5 data
        current_price=data_package.get('current_price', 0),
        m5_trend=data_package.get('m5', {}).get('trend', 'UNKNOWN'),
        m5_ema9=data_package.get('m5', {}).get('ema_9', 0),
        m5_ema21=data_package.get('m5', {}).get('ema_21', 0),
        m5_price_action=data_package.get('m5', {}).get('price_action', 'Unknown'),
        m5_rsi=data_package.get('m5', {}).get('rsi', 50),
        
        # M1 data
        m1_trend=data_package.get('m1', {}).get('trend', 'UNKNOWN'),
        m1_ema9=data_package.get('m1', {}).get('ema_9', 0),
        m1_candles=data_package.get('m1', {}).get('recent_candles', 'No data'),
        m1_momentum=data_package.get('m1', {}).get('momentum', 'NEUTRAL'),
        
        trend_alignment=data_package.get('trend_alignment', 'Unknown'),
        
        # SMC data
        order_blocks_data=ob_text,
        fvg_data=fvg_text,
        market_structure_data=data_package.get('market_structure', {}).get('description', 'Unknown structure'),
        liquidity_data=data_package.get('liquidity_description', 'No liquidity data'),
        
        # Premium/Discount
        premium_discount_zone=data_package.get('premium_discount', {}).get('zone', 'UNKNOWN'),
        premium_discount_percentage=data_package.get('premium_discount', {}).get('percentage', 50),
        range_high=data_package.get('premium_discount', {}).get('range_high', 0),
        range_low=data_package.get('premium_discount', {}).get('range_low', 0),
        premium_discount_analysis=data_package.get('premium_discount', {}).get('description', 'Unknown'),
        
        # Technical indicators
        rsi=data_package.get('indicators', {}).get('rsi', 50),
        rsi_status=data_package.get('indicators', {}).get('rsi_status', 'NEUTRAL'),
        macd=data_package.get('indicators', {}).get('macd', 0),
        macd_signal=data_package.get('indicators', {}).get('macd_signal', 0),
        macd_histogram=data_package.get('indicators', {}).get('macd_histogram', 0),
        stoch_k=data_package.get('indicators', {}).get('stoch_k', 50),
        stoch_d=data_package.get('indicators', {}).get('stoch_d', 50),
        stoch_status=data_package.get('indicators', {}).get('stoch_status', 'NEUTRAL'),
        adx=data_package.get('indicators', {}).get('adx', 25),
        trend_strength=data_package.get('indicators', {}).get('trend_strength', 'MODERATE'),
        ema_alignment=data_package.get('indicators', {}).get('ema_alignment', 'MIXED'),
        atr=data_package.get('indicators', {}).get('atr', 0),
        volatility_level=data_package.get('indicators', {}).get('volatility_level', 'NORMAL'),
        bb_upper=data_package.get('indicators', {}).get('bb_upper', 0),
        bb_middle=data_package.get('indicators', {}).get('bb_middle', 0),
        bb_lower=data_package.get('indicators', {}).get('bb_lower', 0),
        bb_width=data_package.get('indicators', {}).get('bb_width', 0),
        bb_status=data_package.get('indicators', {}).get('bb_status', 'NORMAL'),
        
        # Volume
        volume_analysis=data_package.get('volume', {}).get('analysis', 'No volume data'),
        
        # Recent candles
        recent_candles=recent_candles_text,
        
        # Fundamental
        fundamental_context=data_package.get('fundamental_context', 'No fundamental data')
    )
    
    return prompt


def create_simplified_prompt(symbol: str, current_price: float, trend: str, 
                           session: str, confidence: int) -> str:
    """
    Create a simplified prompt for quick analysis
    Used when full analysis is not needed
    """
    return f"""
    Quick Analysis for {symbol}:
    Current Price: {current_price}
    Trend: {trend}
    Session: {session}
    Confidence: {confidence}%
    
    Provide a brief JSON response with:
    - setup_detected: true/false
    - direction: BUY/SELL/NO_TRADE
    - confidence_score: 0-100
    - reasoning: Brief explanation
    """

