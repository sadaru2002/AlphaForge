import React from 'react';
import moment from 'moment';

const SignalCard = ({ signal }) => {
  const isBuy = signal.direction === 'BUY';
  
  return (
    <div
      className={`bg-gray-800 rounded-lg p-4 border-l-4 ${
        isBuy ? 'border-green-500' : 'border-red-500'
      } hover:bg-gray-750 transition-all`}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="flex items-center space-x-2">
            <span
              className={`text-2xl font-bold ${
                isBuy ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {isBuy ? '🟢' : '🔴'} {signal.direction}
            </span>
            <span className="text-xs bg-blue-600 px-2 py-1 rounded">
              {Math.round(signal.ml_probability * 100)}% Confidence
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            {moment(signal.timestamp).fromNow()}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Entry</p>
          <p className="text-lg font-mono font-bold">{signal.entry.toFixed(5)}</p>
        </div>
      </div>

      {/* Levels */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-gray-900 rounded p-2">
          <p className="text-xs text-red-400">Stop Loss</p>
          <p className="text-sm font-mono">{signal.stop_loss.toFixed(5)}</p>
          <p className="text-xs text-gray-500">{signal.sl_pips.toFixed(1)} pips</p>
        </div>
        <div className="bg-gray-900 rounded p-2">
          <p className="text-xs text-green-400">TP1 (70%)</p>
          <p className="text-sm font-mono">{signal.tp1.toFixed(5)}</p>
          <p className="text-xs text-gray-500">{signal.tp1_pips.toFixed(1)} pips</p>
        </div>
        <div className="bg-gray-900 rounded p-2">
          <p className="text-xs text-green-400">TP2 (30%)</p>
          <p className="text-sm font-mono">{signal.tp2.toFixed(5)}</p>
          <p className="text-xs text-gray-500">{signal.tp2_pips.toFixed(1)} pips</p>
        </div>
      </div>

      {/* Details */}
      <div className="border-t border-gray-700 pt-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Setup:</span>
          <span className="text-blue-400 font-semibold">{signal.setup_type}</span>
        </div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Session:</span>
          <span>{signal.session}</span>
        </div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Confirmations:</span>
          <span className="text-green-400 font-bold">
            {signal.confirmation_score}/9 ✅
          </span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-400">Risk:Reward:</span>
          <span className="text-yellow-400 font-semibold">{signal.rr_ratio}</span>
        </div>
      </div>

      {/* Action Button */}
      <button className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition-colors">
        Copy to Clipboard
      </button>
    </div>
  );
};

export default SignalCard;
