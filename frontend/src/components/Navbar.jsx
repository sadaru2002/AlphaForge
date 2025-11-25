import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = ({ status }) => {
  const location = useLocation();
  const isRunning = Boolean(status?.running);
  const backendStatus = status?.backend || 'offline';
  const isBackendOnline = backendStatus === 'online' && isRunning;

  const navItems = [
    { name: 'Dashboard', path: '/', icon: '🏠' },
    { name: 'Signals', path: '/signals', icon: '📊' },
    { name: 'Journal', path: '/journal', icon: '📚' },
    { name: 'Analytics', path: '/analytics', icon: '📈' },
  ];

  return (
    <nav className="bg-bg-main border-b border-border-subtle h-18 sticky top-0 z-50">
      <div className="w-full px-12 h-full flex items-center justify-end">
        {/* Right Section */}
        <div className="flex items-center gap-6">
          {/* System Status */}
          <div className="flex items-center gap-3 px-6 py-3 bg-bg-card rounded-lg border border-border-subtle min-w-[140px]">
            <div className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-accent-primary animate-pulse-green' : 'bg-accent-danger'
              }`}></div>
            <span className="text-small font-medium text-text-primary">
              {isBackendOnline ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="lg:hidden border-t border-border-subtle">
        <div className="container mx-auto px-4 py-2 flex justify-around">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-smooth ${isActive
                    ? 'bg-accent-primary text-bg-main'
                    : 'text-text-secondary hover:text-text-primary'
                  }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="text-tiny font-medium">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;



