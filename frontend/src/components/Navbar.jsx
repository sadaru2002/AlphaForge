import React from 'react';

const Navbar = ({ status }) => {
  const getStatusColor = (serviceStatus) => {
    if (serviceStatus === 'connected' || serviceStatus === 'online' || serviceStatus === 'running') return 'bg-green-500';
    if (serviceStatus === 'mock' || serviceStatus === 'ready') return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <nav className="h-18 bg-bg-card border-b border-border-subtle px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <h2 className="text-h4 font-semibold text-text-primary">Trading Dashboard</h2>
      </div>

      <div className="flex items-center gap-4">
        {/* System Status */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${getStatusColor(status.backend)}`}></div>
          <span className="text-small text-text-secondary">
            {status.status === 'healthy' ? 'System Online' : 'System Status'}
          </span>
        </div>

        {/* Quick Actions */}
        <button className="px-4 py-2 bg-accent-primary text-bg-main rounded-lg text-small font-semibold hover:bg-green-600 transition-smooth">
          Generate Signals
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
