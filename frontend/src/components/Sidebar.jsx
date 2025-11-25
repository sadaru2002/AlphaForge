import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: '🏠', description: 'Overview & Stats' },
    { name: 'Signals', path: '/signals', icon: '📊', description: 'Live Trade Signals' },
    { name: 'Analytics', path: '/analytics', icon: '📈', description: 'Performance Analysis' },
    { name: 'Trading Journal', path: '/journal', icon: '📚', description: 'Trade History' },
  ];

  return (
    <aside className="hidden lg:flex flex-col w-70 h-screen bg-bg-main border-r border-border-subtle sticky top-0">
      {/* Logo Section */}
      <div className="h-18 flex items-center justify-center border-b border-border-subtle">
        <div className="text-center">
          <h1 className="text-h3 font-bold">
            <span className="text-gradient-green">Alpha</span>
            <span className="text-text-primary">Forge</span>
          </h1>
          <p className="text-tiny text-text-muted mt-1">Trading System</p>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-6 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-6 py-3 rounded-lg transition-smooth ${
                isActive
                  ? 'bg-accent-primary text-bg-main font-semibold'
                  : 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="text-body">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section - User Profile */}
      <div className="p-4 border-t border-border-subtle">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-bg-elevated transition-smooth">
          <div className="w-10 h-10 rounded-full bg-accent-primary flex items-center justify-center text-bg-main font-bold text-h4">
            A
          </div>
          <div className="flex-1 text-left">
            <p className="text-body font-semibold text-text-primary">Admin</p>
            <p className="text-tiny text-text-muted">View Profile</p>
          </div>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
