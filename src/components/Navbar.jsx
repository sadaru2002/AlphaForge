import React from 'react';

const Navbar = ({ status }) => {
  const isRunning = Boolean(status?.running);

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-blue-400 text-2xl font-bold">AlphaForge</div>
          <span className="text-gray-400 hidden sm:inline">GBP/USD Trading Bot</span>
        </div>
        <div className="flex items-center space-x-6">
          <div className="flex items-center text-sm">
            <span
              className={`w-2.5 h-2.5 rounded-full mr-2 ${
                isRunning ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}
            />
            <span className="text-gray-300">{isRunning ? 'Active' : 'Stopped'}</span>
          </div>
          <div className="hidden md:flex items-center space-x-4 text-sm text-gray-300">
            <a className="hover:text-blue-400" href="/">Dashboard</a>
            <a className="hover:text-blue-400" href="/journal">Journal</a>
            <a className="hover:text-blue-400" href="/backtesting">Backtesting</a>
            <a className="hover:text-blue-400" href="#signals">Signals</a>
            <a className="hover:text-blue-400" href="#stats">Stats</a>
            <a className="hover:text-blue-400" href="#chart">Chart</a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;


