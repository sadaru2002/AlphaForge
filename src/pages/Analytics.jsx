import React from 'react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

const Analytics = () => {
  return (
    <div className="flex min-h-screen bg-bg-main">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar status={{}} />
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-h2 font-bold text-text-primary mb-6">📈 Performance Analytics</h1>
            <div className="bg-bg-card border border-border-subtle rounded-lg p-8">
              <p className="text-text-muted text-center">
                Analytics page - View detailed performance metrics and insights
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Analytics;
