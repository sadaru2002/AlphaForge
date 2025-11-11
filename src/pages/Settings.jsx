import React, { useState, useEffect } from 'react';
import { Save, RefreshCw, AlertTriangle, Shield, Bell, Key, Database, Zap, Target, TrendingUp, Clock, DollarSign, Percent, Lock, Unlock, Eye, EyeOff } from 'lucide-react';
import settingsService from '../services/settings';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [showApiKey, setShowApiKey] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingApi, setTestingApi] = useState(false);
  const [settings, setSettings] = useState({
    // General Settings
    botEnabled: true,
    tradingMode: 'live',
    autoTrade: true,
    notifications: true,
    
    // Risk Management
    maxDailyLoss: 500,
    maxDailyTrades: 10,
    riskPerTrade: 1.0,
    stopLossEnabled: true,
    takeProfitEnabled: true,
    trailingStopEnabled: false,
    
    // Trading Parameters
    symbols: ['GBPUSD', 'XAUUSD', 'EURUSD'],
    timeframes: ['5m', '15m', '1h'],
    minRiskReward: 1.5,
    maxPositions: 3,
    
    // Strategy Settings
    strategyName: 'ALGOX ALMA Strategy',
    almaEnabled: true,
    emaEnabled: true,
    rsiEnabled: true,
    macdEnabled: false,
    
    // API Settings
    oandaApiKey: '11bacc1becaf8df27bfd105a828ba70b-c9f535661ccd35bbd1310bffe8b79595',
    oandaAccountId: '101-001-37260967-001',
    oandaEnvironment: 'practice',
    
    // Notification Settings
    emailNotifications: true,
    telegramEnabled: false,
    discordEnabled: false,
    pushNotifications: true,
    
    // Advanced Settings
    slippage: 2,
    maxSpread: 3,
    newsFilter: true,
    sessionFilter: true,
    backtestMode: false,
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await settingsService.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await settingsService.updateSettings(settings);
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleBotToggle = async () => {
    try {
      await settingsService.toggleBot(!settings.botEnabled);
      setSettings(prev => ({ ...prev, botEnabled: !prev.botEnabled }));
    } catch (error) {
      console.error('Error toggling bot:', error);
      alert('Failed to toggle bot. Please try again.');
    }
  };

  const handleTestApiConnection = async () => {
    try {
      setTestingApi(true);
      const credentials = {
        apiKey: settings.oandaApiKey,
        accountId: settings.oandaAccountId,
        environment: settings.oandaEnvironment
      };
      await settingsService.testApiConnection(credentials);
      alert('API connection test successful!');
    } catch (error) {
      console.error('Error testing API connection:', error);
      alert('API connection test failed. Please check your credentials.');
    } finally {
      setTestingApi(false);
    }
  };

  const tabs = [
    { id: 'general', label: 'General', icon: <Target size={18} /> },
    { id: 'risk', label: 'Risk Management', icon: <Shield size={18} /> },
    { id: 'strategy', label: 'Strategy', icon: <TrendingUp size={18} /> },
    { id: 'api', label: 'API Keys', icon: <Key size={18} /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell size={18} /> },
    { id: 'advanced', label: 'Advanced', icon: <Zap size={18} /> },
  ];

  return (
    <div className="min-h-screen bg-bg-main p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-h1 text-gradient-green mb-2">⚙️ Bot Settings</h1>
        <p className="text-body text-text-secondary">
          Configure your trading bot parameters and preferences
        </p>
      </div>

      {/* Status Bar */}
      <div className="bg-bg-card border border-border-subtle rounded-lg p-4 mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className={`w-3 h-3 rounded-full ${settings.botEnabled ? 'bg-accent-primary animate-pulse' : 'bg-accent-danger'}`}></div>
          <span className="text-body text-text-primary font-semibold">
            Bot Status: {settings.botEnabled ? 'Running' : 'Stopped'}
          </span>
          <span className={`px-3 py-1 rounded-full text-small ${
            settings.tradingMode === 'live' 
              ? 'bg-accent-primary/20 text-accent-primary' 
              : 'bg-accent-warning/20 text-accent-warning'
          }`}>
            {settings.tradingMode.toUpperCase()} MODE
          </span>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleBotToggle}
            className={`px-4 py-2 rounded-lg transition-smooth ${
              settings.botEnabled 
                ? 'bg-accent-danger text-white' 
                : 'bg-accent-primary text-bg-main'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading}
          >
            {settings.botEnabled ? 'Stop Bot' : 'Start Bot'}
          </button>
          <button 
            onClick={handleSave} 
            className={`btn-primary flex items-center gap-2 ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={saving}
          >
            {saving ? <RefreshCw className="animate-spin" size={18} /> : <Save size={18} />}
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-bg-card border border-border-subtle rounded-lg overflow-hidden">
        <div className="flex border-b border-border-subtle overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-4 transition-smooth whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-accent-primary text-bg-main font-semibold'
                  : 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <SettingGroup title="Bot Control">
                <ToggleSetting
                  label="Enable Trading Bot"
                  description="Turn the automated trading bot on or off"
                  value={settings.botEnabled}
                  onChange={(val) => handleSettingChange('botEnabled', val)}
                />
                <ToggleSetting
                  label="Auto-Trade"
                  description="Automatically execute signals without confirmation"
                  value={settings.autoTrade}
                  onChange={(val) => handleSettingChange('autoTrade', val)}
                />
                <SelectSetting
                  label="Trading Mode"
                  description="Choose between live trading or paper trading"
                  value={settings.tradingMode}
                  options={[
                    { value: 'live', label: 'Live Trading' },
                    { value: 'paper', label: 'Paper Trading' },
                    { value: 'backtest', label: 'Backtest Only' },
                  ]}
                  onChange={(val) => handleSettingChange('tradingMode', val)}
                />
              </SettingGroup>

              <SettingGroup title="Trading Instruments">
                <MultiSelectSetting
                  label="Enabled Symbols"
                  description="Select symbols to trade"
                  values={settings.symbols}
                  options={['GBPUSD', 'XAUUSD', 'EURUSD', 'USDJPY', 'AUDUSD', 'USDCAD']}
                  onChange={(val) => handleSettingChange('symbols', val)}
                />
                <MultiSelectSetting
                  label="Timeframes"
                  description="Select analysis timeframes"
                  values={settings.timeframes}
                  options={['1m', '5m', '15m', '30m', '1h', '4h', '1d']}
                  onChange={(val) => handleSettingChange('timeframes', val)}
                />
              </SettingGroup>
            </div>
          )}

          {/* Risk Management */}
          {activeTab === 'risk' && (
            <div className="space-y-6">
              <SettingGroup title="Risk Limits">
                <NumberSetting
                  label="Max Daily Loss ($)"
                  description="Stop trading if daily loss exceeds this amount"
                  value={settings.maxDailyLoss}
                  onChange={(val) => handleSettingChange('maxDailyLoss', val)}
                  min={100}
                  max={5000}
                  step={50}
                  icon={<DollarSign size={18} />}
                />
                <NumberSetting
                  label="Max Daily Trades"
                  description="Maximum number of trades per day"
                  value={settings.maxDailyTrades}
                  onChange={(val) => handleSettingChange('maxDailyTrades', val)}
                  min={1}
                  max={50}
                  step={1}
                  icon={<Target size={18} />}
                />
                <NumberSetting
                  label="Risk Per Trade (%)"
                  description="Percentage of account to risk per trade"
                  value={settings.riskPerTrade}
                  onChange={(val) => handleSettingChange('riskPerTrade', val)}
                  min={0.1}
                  max={5}
                  step={0.1}
                  icon={<Percent size={18} />}
                />
                <NumberSetting
                  label="Max Positions"
                  description="Maximum concurrent open positions"
                  value={settings.maxPositions}
                  onChange={(val) => handleSettingChange('maxPositions', val)}
                  min={1}
                  max={10}
                  step={1}
                  icon={<Target size={18} />}
                />
              </SettingGroup>

              <SettingGroup title="Protection Settings">
                <ToggleSetting
                  label="Stop Loss"
                  description="Enable automatic stop loss on all trades"
                  value={settings.stopLossEnabled}
                  onChange={(val) => handleSettingChange('stopLossEnabled', val)}
                />
                <ToggleSetting
                  label="Take Profit"
                  description="Enable automatic take profit on all trades"
                  value={settings.takeProfitEnabled}
                  onChange={(val) => handleSettingChange('takeProfitEnabled', val)}
                />
                <ToggleSetting
                  label="Trailing Stop"
                  description="Enable trailing stop to lock in profits"
                  value={settings.trailingStopEnabled}
                  onChange={(val) => handleSettingChange('trailingStopEnabled', val)}
                />
              </SettingGroup>

              <SettingGroup title="Trade Quality">
                <NumberSetting
                  label="Min Risk/Reward Ratio"
                  description="Minimum risk-reward ratio to accept trades"
                  value={settings.minRiskReward}
                  onChange={(val) => handleSettingChange('minRiskReward', val)}
                  min={1}
                  max={5}
                  step={0.1}
                  icon={<TrendingUp size={18} />}
                />
              </SettingGroup>
            </div>
          )}

          {/* Strategy Settings */}
          {activeTab === 'strategy' && (
            <div className="space-y-6">
              <SettingGroup title="Active Strategy">
                <div className="bg-bg-elevated rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-h4 text-text-primary">{settings.strategyName}</h4>
                    <span className="px-3 py-1 bg-accent-primary/20 text-accent-primary rounded-full text-small">
                      Active
                    </span>
                  </div>
                  <p className="text-body text-text-secondary">
                    ALMA-based strategy with multiple timeframe confirmation
                  </p>
                </div>
              </SettingGroup>

              <SettingGroup title="Technical Indicators">
                <ToggleSetting
                  label="ALMA (Arnaud Legoux Moving Average)"
                  description="Primary trend indicator"
                  value={settings.almaEnabled}
                  onChange={(val) => handleSettingChange('almaEnabled', val)}
                />
                <ToggleSetting
                  label="EMA (Exponential Moving Average)"
                  description="Trend confirmation"
                  value={settings.emaEnabled}
                  onChange={(val) => handleSettingChange('emaEnabled', val)}
                />
                <ToggleSetting
                  label="RSI (Relative Strength Index)"
                  description="Overbought/oversold detection"
                  value={settings.rsiEnabled}
                  onChange={(val) => handleSettingChange('rsiEnabled', val)}
                />
                <ToggleSetting
                  label="MACD (Moving Average Convergence Divergence)"
                  description="Momentum indicator"
                  value={settings.macdEnabled}
                  onChange={(val) => handleSettingChange('macdEnabled', val)}
                />
              </SettingGroup>
            </div>
          )}

          {/* API Settings */}
          {activeTab === 'api' && (
            <div className="space-y-6">
              <div className="bg-accent-warning/10 border border-accent-warning/30 rounded-lg p-4 flex items-start gap-3 mb-6">
                <AlertTriangle className="text-accent-warning mt-1" size={20} />
                <div>
                  <h4 className="text-body font-semibold text-accent-warning mb-1">Security Warning</h4>
                  <p className="text-small text-text-secondary">
                    Never share your API keys. Keep them secure and rotate them regularly.
                  </p>
                </div>
              </div>

              <SettingGroup title="OANDA API Configuration">
                <TextSetting
                  label="API Key"
                  description="Your OANDA API access token"
                  value={settings.oandaApiKey}
                  onChange={(val) => handleSettingChange('oandaApiKey', val)}
                  type={showApiKey ? 'text' : 'password'}
                  icon={<Key size={18} />}
                  action={
                    <button
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="text-accent-primary hover:text-accent-primary/80"
                    >
                      {showApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  }
                />
                <TextSetting
                  label="Account ID"
                  description="Your OANDA account identifier"
                  value={settings.oandaAccountId}
                  onChange={(val) => handleSettingChange('oandaAccountId', val)}
                  icon={<Database size={18} />}
                />
                <SelectSetting
                  label="Environment"
                  description="Trading environment"
                  value={settings.oandaEnvironment}
                  options={[
                    { value: 'practice', label: 'Practice (Demo)' },
                    { value: 'live', label: 'Live (Real Money)' },
                  ]}
                  onChange={(val) => handleSettingChange('oandaEnvironment', val)}
                />
              </SettingGroup>

              <button 
                onClick={handleTestApiConnection}
                className={`btn-secondary w-full flex items-center justify-center gap-2 ${testingApi ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={testingApi}
              >
                {testingApi ? <RefreshCw className="animate-spin" size={18} /> : <RefreshCw size={18} />}
                {testingApi ? 'Testing Connection...' : 'Test API Connection'}
              </button>
            </div>
          )}

          {/* Notifications */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <SettingGroup title="Notification Channels">
                <ToggleSetting
                  label="Email Notifications"
                  description="Receive trade alerts via email"
                  value={settings.emailNotifications}
                  onChange={(val) => handleSettingChange('emailNotifications', val)}
                />
                <ToggleSetting
                  label="Telegram Alerts"
                  description="Send signals to Telegram bot"
                  value={settings.telegramEnabled}
                  onChange={(val) => handleSettingChange('telegramEnabled', val)}
                />
                <ToggleSetting
                  label="Discord Webhooks"
                  description="Post signals to Discord channel"
                  value={settings.discordEnabled}
                  onChange={(val) => handleSettingChange('discordEnabled', val)}
                />
                <ToggleSetting
                  label="Push Notifications"
                  description="Browser push notifications"
                  value={settings.pushNotifications}
                  onChange={(val) => handleSettingChange('pushNotifications', val)}
                />
              </SettingGroup>
            </div>
          )}

          {/* Advanced Settings */}
          {activeTab === 'advanced' && (
            <div className="space-y-6">
              <SettingGroup title="Execution Settings">
                <NumberSetting
                  label="Max Slippage (pips)"
                  description="Maximum acceptable slippage"
                  value={settings.slippage}
                  onChange={(val) => handleSettingChange('slippage', val)}
                  min={0}
                  max={10}
                  step={0.5}
                />
                <NumberSetting
                  label="Max Spread (pips)"
                  description="Don't trade if spread exceeds this"
                  value={settings.maxSpread}
                  onChange={(val) => handleSettingChange('maxSpread', val)}
                  min={1}
                  max={20}
                  step={1}
                />
              </SettingGroup>

              <SettingGroup title="Filters">
                <ToggleSetting
                  label="News Filter"
                  description="Avoid trading during high-impact news events"
                  value={settings.newsFilter}
                  onChange={(val) => handleSettingChange('newsFilter', val)}
                />
                <ToggleSetting
                  label="Session Filter"
                  description="Only trade during specific market sessions"
                  value={settings.sessionFilter}
                  onChange={(val) => handleSettingChange('sessionFilter', val)}
                />
                <ToggleSetting
                  label="Backtest Mode"
                  description="Enable for strategy testing (no real trades)"
                  value={settings.backtestMode}
                  onChange={(val) => handleSettingChange('backtestMode', val)}
                />
              </SettingGroup>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Helper Components
const SettingGroup = ({ title, children }) => (
  <div>
    <h3 className="text-h4 text-text-primary mb-4">{title}</h3>
    <div className="space-y-4">
      {children}
    </div>
  </div>
);

const ToggleSetting = ({ label, description, value, onChange }) => (
  <div className="flex items-center justify-between p-4 bg-bg-elevated rounded-lg">
    <div className="flex-1">
      <h4 className="text-body text-text-primary font-semibold mb-1">{label}</h4>
      <p className="text-small text-text-secondary">{description}</p>
    </div>
    <button
      onClick={() => onChange(!value)}
      className={`relative w-14 h-7 rounded-full transition-colors ${
        value ? 'bg-accent-primary' : 'bg-bg-card border border-border-subtle'
      }`}
    >
      <span
        className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${
          value ? 'translate-x-7' : 'translate-x-0'
        }`}
      />
    </button>
  </div>
);

const NumberSetting = ({ label, description, value, onChange, min, max, step, icon }) => (
  <div className="p-4 bg-bg-elevated rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      {icon}
      <h4 className="text-body text-text-primary font-semibold">{label}</h4>
    </div>
    <p className="text-small text-text-secondary mb-3">{description}</p>
    <div className="flex items-center gap-4">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1 accent-accent-primary"
      />
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-24 px-3 py-2 bg-bg-card border border-border-subtle rounded-lg text-text-primary"
      />
    </div>
  </div>
);

const SelectSetting = ({ label, description, value, options, onChange }) => (
  <div className="p-4 bg-bg-elevated rounded-lg">
    <h4 className="text-body text-text-primary font-semibold mb-1">{label}</h4>
    <p className="text-small text-text-secondary mb-3">{description}</p>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-2 bg-bg-card border border-border-subtle rounded-lg text-text-primary"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  </div>
);

const TextSetting = ({ label, description, value, onChange, type = 'text', icon, action }) => (
  <div className="p-4 bg-bg-elevated rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      {icon}
      <h4 className="text-body text-text-primary font-semibold">{label}</h4>
    </div>
    <p className="text-small text-text-secondary mb-3">{description}</p>
    <div className="flex items-center gap-2">
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="flex-1 px-4 py-2 bg-bg-card border border-border-subtle rounded-lg text-text-primary font-mono text-small"
      />
      {action}
    </div>
  </div>
);

const MultiSelectSetting = ({ label, description, values, options, onChange }) => (
  <div className="p-4 bg-bg-elevated rounded-lg">
    <h4 className="text-body text-text-primary font-semibold mb-1">{label}</h4>
    <p className="text-small text-text-secondary mb-3">{description}</p>
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isSelected = values.includes(option);
        return (
          <button
            key={option}
            onClick={() => {
              if (isSelected) {
                onChange(values.filter((v) => v !== option));
              } else {
                onChange([...values, option]);
              }
            }}
            className={`px-4 py-2 rounded-lg transition-smooth ${
              isSelected
                ? 'bg-accent-primary text-bg-main'
                : 'bg-bg-card text-text-secondary hover:bg-bg-hover'
            }`}
          >
            {option}
          </button>
        );
      })}
    </div>
  </div>
);

export default Settings;
