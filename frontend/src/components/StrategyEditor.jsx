import React, { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const StrategyEditor = ({ onSave, onValidate, initialCode = '' }) => {
  const [code, setCode] = useState(initialCode);
  const [isValid, setIsValid] = useState(false);
  const [validationMessage, setValidationMessage] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  // Default strategy template
  const defaultStrategy = `import pandas as pd
import numpy as np

def generate_signals(df):
    """
    User-defined strategy function.
    
    Input: df (DataFrame with OHLCV data)
    Output: DataFrame with 'signal' column (BUY, SELL, HOLD)
            and 'confidence' column (0-100)
    """
    
    # Example: Simple MA crossover with confidence
    df['sma_9'] = df['close'].rolling(9).mean()
    df['sma_21'] = df['close'].rolling(21).mean()
    
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 'HOLD'
    signals['confidence'] = 0
    signals['entry'] = df['close']
    signals['stop_loss'] = 0
    signals['take_profit'] = 0
    signals['predicted_pips'] = 0
    signals['risk_reward'] = 0
    
    # BUY signal
    buy_mask = (df['sma_9'] > df['sma_21']) & (df['sma_9'].shift(1) <= df['sma_21'].shift(1))
    signals.loc[buy_mask, 'signal'] = 'BUY'
    signals.loc[buy_mask, 'confidence'] = 75  # 75% confidence
    signals.loc[buy_mask, 'stop_loss'] = df.loc[buy_mask, 'close'] * 0.98
    signals.loc[buy_mask, 'take_profit'] = df.loc[buy_mask, 'close'] * 1.02
    signals.loc[buy_mask, 'predicted_pips'] = 200
    signals.loc[buy_mask, 'risk_reward'] = 2.0
    
    # SELL signal
    sell_mask = (df['sma_9'] < df['sma_21']) & (df['sma_9'].shift(1) >= df['sma_21'].shift(1))
    signals.loc[sell_mask, 'signal'] = 'SELL'
    signals.loc[sell_mask, 'confidence'] = 72
    signals.loc[sell_mask, 'stop_loss'] = df.loc[sell_mask, 'close'] * 1.02
    signals.loc[sell_mask, 'take_profit'] = df.loc[sell_mask, 'close'] * 0.98
    signals.loc[sell_mask, 'predicted_pips'] = -200
    signals.loc[sell_mask, 'risk_reward'] = 2.0
    
    return signals.dropna()`;

  useEffect(() => {
    if (!code) {
      setCode(defaultStrategy);
    }
  }, []);

  const handleValidate = async () => {
    setIsValidating(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://161.118.218.33:5000'}/api/backtest/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ strategy_code: code }),
      });
      
      const result = await response.json();
      
      if (result.valid) {
        setIsValid(true);
        setValidationMessage(result.message);
      } else {
        setIsValid(false);
        setValidationMessage(result.error || 'Validation failed');
      }
    } catch (error) {
      setIsValid(false);
      setValidationMessage('Error validating strategy');
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = () => {
    if (isValid && onSave) {
      onSave(code);
    }
  };

  return (
    <div className="strategy-editor">
      <div className="editor-header">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Strategy Editor</h3>
        <div className="flex gap-2 mb-4">
          <button
            onClick={handleValidate}
            disabled={isValidating}
            className={`px-4 py-2 rounded ${
              isValidating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isValidating ? 'Validating...' : 'Validate Code'}
          </button>
          <button
            onClick={handleSave}
            disabled={!isValid}
            className={`px-4 py-2 rounded ${
              !isValid
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            Save Strategy
          </button>
        </div>
        {validationMessage && (
          <div className={`p-3 rounded mb-4 ${
            isValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {validationMessage}
          </div>
        )}
      </div>
      
      <div className="editor-container">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full h-96 p-4 border border-gray-300 rounded font-mono text-sm"
          placeholder="Enter your Python strategy code here..."
        />
      </div>
      
      <div className="editor-footer mt-4">
        <h4 className="text-lg font-semibold text-gray-700 mb-2">Strategy Requirements:</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Must define a <code className="bg-gray-100 px-1 rounded">generate_signals(df)</code> function</li>
          <li>• Function must return a DataFrame with 'signal' column (BUY, SELL, HOLD)</li>
          <li>• Optional: 'confidence' column (0-100), 'entry', 'stop_loss', 'take_profit'</li>
          <li>• Input DataFrame has columns: open, high, low, close, volume</li>
          <li>• Use pandas and numpy for technical analysis</li>
        </ul>
      </div>
    </div>
  );
};

export default StrategyEditor;
