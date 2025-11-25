# Signal Generation Fix - November 13, 2025

## Problem Identified

**No signals were being generated** due to a **threshold mismatch** between voting requirements and strength calculation.

### Root Cause

1. **Voting threshold**: `min_votes_required = 1.5` (allows signals with 1.5+ indicator votes)
2. **Strength calculation**: `strength = (votes / 6.0) * 100`
   - 1.5 votes → 25% strength
   - 1.75 votes → 29.2% strength
   - 1.8 votes → 30% strength
3. **Strength threshold**: `min_strength = 30%` (required 1.8+ votes to pass)

**Result**: Signals with 1.5-1.79 votes passed voting but failed strength filter!

### Evidence from Rejection Report (2025-11-12)

```
Total Rejections: 36
- Strength failures: 18 (signals with 1.75 votes = 29.2% strength < 30% threshold)
- No signal generated: 18 (votes below 1.5)

Example:
GBP_USD @ 00:00
  Buy votes: 1.75, Sell votes: 1.15
  Calculated strength: 29.2%
  Rejection: "Signal strength too weak: 29.2% (need 30.0%+)"
```

## Solution Applied

### 1. Aligned min_strength with min_votes_required

**File**: `backend/multi_timeframe_engine.py`

**Change**: Lowered `min_strength` from 30.0% to 25.0%

```python
def __init__(self, api_key=None, environment="practice", 
             min_votes_required=1.5, min_strength=25.0):  # Changed from 30.0
```

**Rationale**: 
- 1.5 votes = 25% strength
- Now thresholds are mathematically aligned
- Signals with 1.5+ votes will pass both voting AND strength filters

### 2. Updated EnhancedSignalGenerator

**File**: `backend/enhanced_signal_generator.py`

**Change**: Lowered strength check from 30% to 25%

```python
if mtf_signal['strength'] < 25:  # Changed from 30
    # Reject signal
```

### 3. Improved strength calculation for NO_ACTION cases

**File**: `backend/multi_timeframe_engine.py`

**Change**: NO_ACTION signals now show actual strength for debugging

```python
else:
    signal_type = 'NO_ACTION'
    max_votes = max(avg_buy_votes, avg_sell_votes)
    strength = (max_votes / 6.0) * 100  # Was: 0.0
```

## Test Results

**Test**: `test_threshold_fix.py`

```
✅ GBP_USD: SIGNAL GENERATED (SELL)
✅ XAU_USD: SIGNAL GENERATED (SELL)
✅ USD_JPY: SIGNAL GENERATED (SELL)
```

**Verification**: All 3 instruments now successfully generate signals!

## Current Filter Configuration

### Voting & Strength
- `min_votes_required`: 1.5 (out of 6 indicators)
- `min_strength`: 25% (aligned with 1.5 votes)

### Volatility (ATR%)
- Min: 0.01%
- Max: 0.50%
- (Previously: 0.05% - 0.25%)

### Trend Strength (ADX)
- Min: 10
- (Previously: 15)

### Agreement
- Min: 0.5 (50% timeframe alignment)
- (Previously: 0.67)

### Regime Filters
- ✅ Allows transitional regimes
- ✅ All regime types tradeable

## Expected Signal Frequency

With these settings:
- **Before fix**: 0 signals (threshold mismatch)
- **After fix**: ~2-4 signals/day per instrument (estimated)
- **Quality**: Medium (balanced between quantity and quality)

## Recommendations

1. **Monitor for 24-48 hours** to see actual signal frequency
2. **If too many signals**: Raise `min_strength` to 27-28%
3. **If still too few**: Lower `min_votes_required` to 1.3
4. **Track win rate**: Adjust thresholds based on backtest results

## Files Modified

1. `backend/multi_timeframe_engine.py`
   - Changed `min_strength` default: 30.0 → 25.0
   - Updated docstring
   - Improved NO_ACTION strength calculation

2. `backend/enhanced_signal_generator.py`
   - Changed strength check: 30 → 25
   - Updated rejection message

3. **Created**:
   - `backend/analyze_rejections.py` (diagnostic tool)
   - `backend/test_threshold_fix.py` (verification test)
   - `SIGNAL_GENERATION_FIX.md` (this document)

## Next Steps

1. ✅ Fix applied and tested
2. ⏭️ Restart backend to load new thresholds
3. ⏭️ Run "yesterday" generator to verify real signal generation
4. ⏭️ Monitor signal quality over next 24h
5. ⏭️ Adjust thresholds if needed based on performance

---

**Status**: ✅ **FIXED** - Signals now generate successfully!

**Date**: November 13, 2025
