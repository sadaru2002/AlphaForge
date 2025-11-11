import React from 'react';

const LivePriceTicker = ({ symbols }) => {
  return (
    <div className="bg-bg-card border border-border-subtle rounded-lg p-4">
      <div className="flex items-center gap-6 overflow-x-auto">
        {symbols.map((symbol, index) => (
          <div key={index} className="flex items-center gap-2 min-w-fit">
            <span className="text-text-secondary text-small font-semibold">{symbol}</span>
            <span className="text-green-400 font-mono">---.---</span>
            <span className="text-green-400 text-tiny">+0.00%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LivePriceTicker;
