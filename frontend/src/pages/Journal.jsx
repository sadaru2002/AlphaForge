import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { format } from 'date-fns';
import { Download, Plus, Trash2, FileDown, FileSpreadsheet, Image, X, Save, Upload, TrendingUp, TrendingDown, Target, Award, Activity, DollarSign, Percent, BarChart3 } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import apiService from '../services/api';

const Journal = () => {
  const [rowData, setRowData] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [filters, setFilters] = useState({
    pair: 'ALL',
    setup: 'ALL',
    session: 'ALL',
    from: format(new Date(), 'yyyy-MM-01'),
    to: format(new Date(), 'yyyy-MM-dd')
  });
  const gridRef = useRef(null);

  // Currency pairs
  const PAIRS = ['GBPUSD', 'EURUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'XAUUSD', 'NZDUSD', 'USDCHF'];
  const SETUPS = ['Breakout', 'Pullback', 'Reversal', 'Trend Following', 'Range Trading', 'News Trading'];
  const SESSIONS = ['LONDON', 'NEW_YORK', 'ASIAN', 'OVERLAP'];

  // Column definitions with delete button
  const columnDefs = useMemo(() => ([
    { 
      headerName: '', 
      field: 'actions',
      width: 60,
      cellRenderer: (params) => (
        <button
          onClick={() => handleDelete(params.data.id)}
          className="text-red-500 hover:text-red-400 p-1"
          title="Delete"
        >
          <Trash2 size={16} />
        </button>
      ),
      pinned: 'left'
    },
    { headerName: 'Open Time', field: 'openTime', sortable: true, filter: 'agDateColumnFilter', editable: true, width: 150 },
    { headerName: 'Type', field: 'type', sortable: true, filter: true, editable: true, width: 90 },
    { headerName: 'Lots', field: 'lots', sortable: true, filter: true, editable: true, width: 90 },
    { headerName: 'Symbol', field: 'symbol', sortable: true, filter: true, editable: true, width: 110 },
    { headerName: 'Entry', field: 'entry', sortable: true, filter: true, editable: true, width: 110 },
    { headerName: 'S/L', field: 'sl', sortable: true, filter: true, editable: true, width: 100 },
    { headerName: 'T/P', field: 'tp', sortable: true, filter: true, editable: true, width: 100 },
    { headerName: 'Close Time', field: 'closeTime', sortable: true, filter: 'agDateColumnFilter', editable: true, width: 150 },
    { headerName: 'Exit', field: 'exit', sortable: true, filter: true, editable: true, width: 110 },
    { headerName: 'Pips', field: 'pips', sortable: true, filter: true, editable: true, width: 90 },
    { headerName: 'P/L', field: 'pl', sortable: true, filter: true, editable: true, width: 100 },
    { headerName: 'MAE', field: 'mae', sortable: true, filter: true, editable: true, width: 90 },
    { headerName: 'Duration', field: 'duration', sortable: true, filter: true, editable: true, width: 110 },
    { headerName: 'R-Value', field: 'r', sortable: true, filter: true, editable: true, width: 100 },
    { headerName: 'Setup', field: 'setup', sortable: true, filter: true, editable: true, width: 140 },
    { headerName: 'Session', field: 'session', sortable: true, filter: true, editable: true, width: 110 },
    { 
      headerName: 'Screenshot', 
      field: 'screenshot_entry',
      width: 110,
      cellRenderer: (params) => (
        params.value ? (
          <button
            onClick={() => viewScreenshot(params.value)}
            className="text-blue-500 hover:text-blue-400 flex items-center gap-1"
          >
            <Image size={14} />
            View
          </button>
        ) : (
          <span className="text-gray-500 text-xs">No image</span>
        )
      )
    },
  ]), []);

  const defaultColDef = useMemo(() => ({ 
    resizable: true, 
    minWidth: 90,
    suppressHeaderMenuButton: true,
    flex: 0
  }), []);

  // Load journal entries from database
  useEffect(() => {
    loadJournalEntries();
    loadStatistics();
  }, []);

  const loadJournalEntries = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/journal/entries');
      const data = await response.json();
      setRowData(data.entries || []);
    } catch (error) {
      console.error('Failed to load journal entries:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/journal/statistics');
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this trade?')) return;
    
    try {
      await fetch(`http://localhost:5000/api/journal/entries/${id}`, {
        method: 'DELETE'
      });
      loadJournalEntries(); // Reload data
      loadStatistics(); // Reload statistics
    } catch (error) {
      console.error('Failed to delete entry:', error);
      alert('Failed to delete entry');
    }
  };

  const viewScreenshot = (base64) => {
    // Open screenshot in new window
    const win = window.open();
    win.document.write(`<img src="${base64}" style="max-width:100%"/>`);
  };

  const filteredRowData = useMemo(() => {
    return rowData.filter((r) => {
      const d = r.openTime ? r.openTime.split(' ')[0] : '';
      const inDate = (!filters.from || d >= filters.from) && (!filters.to || d <= filters.to);
      const byPair = filters.pair === 'ALL' || r.symbol === filters.pair;
      const bySetup = filters.setup === 'ALL' || r.setup === filters.setup;
      const bySession = filters.session === 'ALL' || r.session === filters.session;
      return inDate && byPair && bySetup && bySession;
    });
  }, [rowData, filters]);

  const downloadFile = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const onExportCSV = () => {
    const headers = ['Open Time','Type','Lots','Symbol','Entry','S/L','T/P','Close Time','Exit','Pips','P/L','MAE','Duration','R-Value','Setup','Session'];
    const lines = [headers.join(',')];
    filteredRowData.forEach((r) => {
      const row = [r.openTime,r.type,r.lots,r.symbol,r.entry,r.sl,r.tp,r.closeTime,r.exit,r.pips,r.pl,r.mae,r.duration,r.r,r.setup,r.session]
        .map((v) => (v == null ? '' : String(v).includes(',') ? `"${String(v)}"` : String(v)));
      lines.push(row.join(','));
    });
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    downloadFile(blob, `journal-${filters.from}-${filters.to}.csv`);
  };

  const onExportExcel = async () => {
    const xlsx = await import('xlsx');
    const ws = xlsx.utils.json_to_sheet(filteredRowData);
    const wb = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(wb, ws, 'Trades');
    const wbout = xlsx.write(wb, { type: 'array', bookType: 'xlsx' });
    const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    downloadFile(blob, `journal-${filters.from}-${filters.to}.xlsx`);
  };

  const onExportPDF = () => {
    const doc = new jsPDF('l');
    doc.setFontSize(16);
    doc.text('Trading Journal', 14, 15);
    doc.setFontSize(10);
    doc.text(`Period: ${filters.from} to ${filters.to}`, 14, 22);
    
    const tableData = filteredRowData.map((r) => [
      r.openTime, r.type, r.lots, r.symbol, r.entry, r.sl, r.tp,
      r.closeTime, r.exit, r.pips, r.pl, r.mae, r.duration, r.r, r.setup
    ]);
    
    doc.autoTable({
      startY: 28,
      head: [['Open','Type','Lots','Symbol','Entry','S/L','T/P','Close','Exit','Pips','P/L','MAE','Duration','R','Setup']],
      body: tableData,
      styles: { fontSize: 7 },
      headStyles: { fillColor: [16, 185, 129] }
    });
    
    doc.save(`journal-${filters.from}-${filters.to}.pdf`);
  };

  // Mathematical calculation functions
  const calculateAverageWin = (trades) => {
    const wins = trades.filter(t => (t.pl || t.profit_loss || 0) > 0);
    if (wins.length === 0) return 0;
    const total = wins.reduce((sum, t) => sum + (t.pl || t.profit_loss || 0), 0);
    return total / wins.length;
  };

  const calculateAverageLoss = (trades) => {
    const losses = trades.filter(t => (t.pl || t.profit_loss || 0) < 0);
    if (losses.length === 0) return 0;
    const total = losses.reduce((sum, t) => sum + (t.pl || t.profit_loss || 0), 0);
    return total / losses.length;
  };

  const calculateGrossProfit = (trades) => {
    return trades.filter(t => (t.pl || t.profit_loss || 0) > 0)
      .reduce((sum, t) => sum + (t.pl || t.profit_loss || 0), 0);
  };

  const calculateGrossLoss = (trades) => {
    return trades.filter(t => (t.pl || t.profit_loss || 0) < 0)
      .reduce((sum, t) => sum + (t.pl || t.profit_loss || 0), 0);
  };

  const calculateProfitFactor = (trades) => {
    const grossProfit = calculateGrossProfit(trades);
    const grossLoss = Math.abs(calculateGrossLoss(trades));
    if (grossLoss === 0) return grossProfit > 0 ? 999 : 0;
    return grossProfit / grossLoss;
  };

  const calculateExpectancy = (trades, stats) => {
    if (!stats || trades.length === 0) return 0;
    const winRate = (stats.win_rate || 0) / 100;
    const avgWin = calculateAverageWin(trades);
    const avgLoss = Math.abs(calculateAverageLoss(trades));
    return (winRate * avgWin) - ((1 - winRate) * avgLoss);
  };

  const calculateAverageWinPips = (trades) => {
    const wins = trades.filter(t => (t.pips || 0) > 0);
    if (wins.length === 0) return 0;
    return wins.reduce((sum, t) => sum + (t.pips || 0), 0) / wins.length;
  };

  const calculateAverageLossPips = (trades) => {
    const losses = trades.filter(t => (t.pips || 0) < 0);
    if (losses.length === 0) return 0;
    return losses.reduce((sum, t) => sum + (t.pips || 0), 0) / losses.length;
  };

  const calculateRiskRewardRatio = (trades) => {
    const avgWinPips = calculateAverageWinPips(trades);
    const avgLossPips = Math.abs(calculateAverageLossPips(trades));
    if (avgLossPips === 0) return avgWinPips > 0 ? 999 : 0;
    return avgWinPips / avgLossPips;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gradient-green">📖 Trading Journal</h1>
        <div className="flex gap-3">
          <button onClick={() => setShowAddModal(true)} className="btn-primary flex items-center gap-2">
            <Plus size={18} />
            Add Trade
          </button>
          <button onClick={onExportCSV} className="btn-secondary flex items-center gap-2">
            <FileDown size={18} />
            CSV
          </button>
          <button onClick={onExportExcel} className="btn-secondary flex items-center gap-2">
            <FileSpreadsheet size={18} />
            Excel
          </button>
          <button onClick={onExportPDF} className="btn-secondary flex items-center gap-2">
            <Download size={18} />
            PDF
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <label className="block text-sm text-text-secondary mb-1">From</label>
          <input
            type="date"
            value={filters.from}
            onChange={(e) => setFilters({...filters, from: e.target.value})}
            className="w-full px-4 py-2.5 rounded-lg transition-all"
            style={{
              backgroundColor: '#1A1F2E',
              border: '1px solid #334155',
              color: '#FFFFFF'
            }}
          />
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">To</label>
          <input
            type="date"
            value={filters.to}
            onChange={(e) => setFilters({...filters, to: e.target.value})}
            className="w-full px-4 py-2.5 rounded-lg transition-all"
            style={{
              backgroundColor: '#1A1F2E',
              border: '1px solid #334155',
              color: '#FFFFFF'
            }}
          />
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Pair</label>
          <select
            value={filters.pair}
            onChange={(e) => setFilters({...filters, pair: e.target.value})}
            className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
            style={{
              backgroundColor: '#1A1F2E',
              border: '1px solid #334155',
              color: '#FFFFFF'
            }}
          >
            <option value="ALL" style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>All Pairs</option>
            {PAIRS.map(p => <option key={p} value={p} style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>{p}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Setup</label>
          <select
            value={filters.setup}
            onChange={(e) => setFilters({...filters, setup: e.target.value})}
            className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
            style={{
              backgroundColor: '#1A1F2E',
              border: '1px solid #334155',
              color: '#FFFFFF'
            }}
          >
            <option value="ALL" style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>All Setups</option>
            {SETUPS.map(s => <option key={s} value={s} style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Session</label>
          <select
            value={filters.session}
            onChange={(e) => setFilters({...filters, session: e.target.value})}
            className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
            style={{
              backgroundColor: '#1A1F2E',
              border: '1px solid #334155',
              color: '#FFFFFF'
            }}
          >
            <option value="ALL" style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>All Sessions</option>
            {SESSIONS.map(s => <option key={s} value={s} style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* Statistics Infographics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Total Trades */}
          <div className="card p-4 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Total Trades</p>
                <p className="text-3xl font-bold text-white mt-1">{statistics.total_trades || 0}</p>
              </div>
              <div className="bg-blue-500/20 p-3 rounded-full">
                <Activity size={24} className="text-blue-500" />
              </div>
            </div>
          </div>

          {/* Win Rate */}
          <div className="card p-4 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Win Rate</p>
                <p className="text-3xl font-bold text-green-500 mt-1">
                  {statistics.win_rate ? statistics.win_rate.toFixed(1) : 0}%
                </p>
                <p className="text-xs text-text-secondary mt-1">
                  {statistics.wins || 0}W / {statistics.losses || 0}L
                </p>
              </div>
              <div className="bg-green-500/20 p-3 rounded-full">
                <Target size={24} className="text-green-500" />
              </div>
            </div>
          </div>

          {/* Total P&L */}
          <div className={`card p-4 border-l-4 ${(statistics.total_pnl || 0) >= 0 ? 'border-green-500' : 'border-red-500'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Total P&L</p>
                <p className={`text-3xl font-bold mt-1 ${(statistics.total_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${statistics.total_pnl ? statistics.total_pnl.toFixed(2) : '0.00'}
                </p>
              </div>
              <div className={`${(statistics.total_pnl || 0) >= 0 ? 'bg-green-500/20' : 'bg-red-500/20'} p-3 rounded-full`}>
                {(statistics.total_pnl || 0) >= 0 ? (
                  <TrendingUp size={24} className="text-green-500" />
                ) : (
                  <TrendingDown size={24} className="text-red-500" />
                )}
              </div>
            </div>
          </div>

          {/* Average R-Value */}
          <div className="card p-4 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Avg R-Value</p>
                <p className="text-3xl font-bold text-purple-500 mt-1">
                  {statistics.avg_r ? statistics.avg_r.toFixed(2) : '0.00'}R
                </p>
                <p className="text-xs text-text-secondary mt-1">
                  {statistics.total_pips ? statistics.total_pips.toFixed(1) : 0} pips
                </p>
              </div>
              <div className="bg-purple-500/20 p-3 rounded-full">
                <Award size={24} className="text-purple-500" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Advanced Mathematical Statistics */}
      {statistics && filteredRowData.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Expectancy */}
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 size={20} className="text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Expectancy</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Average Win:</span>
                <span className="text-sm font-semibold text-green-500">
                  ${calculateAverageWin(filteredRowData).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Average Loss:</span>
                <span className="text-sm font-semibold text-red-500">
                  ${calculateAverageLoss(filteredRowData).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-dark-border">
                <span className="text-sm font-semibold text-text-secondary">Expectancy:</span>
                <span className={`text-lg font-bold ${calculateExpectancy(filteredRowData, statistics) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${calculateExpectancy(filteredRowData, statistics).toFixed(2)}
                </span>
              </div>
              <p className="text-xs text-text-secondary italic mt-2">
                Expected profit per trade
              </p>
            </div>
          </div>

          {/* Profit Factor */}
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <DollarSign size={20} className="text-green-400" />
              <h3 className="text-lg font-semibold text-white">Profit Factor</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Gross Profit:</span>
                <span className="text-sm font-semibold text-green-500">
                  ${calculateGrossProfit(filteredRowData).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Gross Loss:</span>
                <span className="text-sm font-semibold text-red-500">
                  ${Math.abs(calculateGrossLoss(filteredRowData)).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-dark-border">
                <span className="text-sm font-semibold text-text-secondary">Profit Factor:</span>
                <span className={`text-lg font-bold ${calculateProfitFactor(filteredRowData) >= 1 ? 'text-green-500' : 'text-red-500'}`}>
                  {calculateProfitFactor(filteredRowData).toFixed(2)}
                </span>
              </div>
              <p className="text-xs text-text-secondary italic mt-2">
                {calculateProfitFactor(filteredRowData) >= 2 ? 'Excellent!' : calculateProfitFactor(filteredRowData) >= 1.5 ? 'Good' : 'Need improvement'}
              </p>
            </div>
          </div>

          {/* Risk/Reward Ratio */}
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <Percent size={20} className="text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Risk/Reward</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Avg Win Pips:</span>
                <span className="text-sm font-semibold text-green-500">
                  {calculateAverageWinPips(filteredRowData).toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Avg Loss Pips:</span>
                <span className="text-sm font-semibold text-red-500">
                  {Math.abs(calculateAverageLossPips(filteredRowData)).toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-dark-border">
                <span className="text-sm font-semibold text-text-secondary">RR Ratio:</span>
                <span className="text-lg font-bold text-purple-500">
                  1:{calculateRiskRewardRatio(filteredRowData).toFixed(2)}
                </span>
              </div>
              <p className="text-xs text-text-secondary italic mt-2">
                {calculateRiskRewardRatio(filteredRowData) >= 2 ? 'Strong RR!' : calculateRiskRewardRatio(filteredRowData) >= 1.5 ? 'Good RR' : 'Improve RR'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Trade Log Table - Full Width */}
      <div className="card p-6">
        <h2 className="text-xl font-bold text-gradient-green mb-4">Trade Log ({filteredRowData.length} trades)</h2>
        <div className="ag-theme-alpine-dark" style={{ height: 'calc(100vh - 380px)', width: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={filteredRowData}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            pagination={true}
            paginationPageSize={20}
            domLayout="normal"
          />
        </div>
      </div>

      {/* Add Trade Modal */}
      {showAddModal && (
        <AddTradeModal
          onClose={() => setShowAddModal(false)}
          onSave={() => {
            loadJournalEntries();
            loadStatistics();
          }}
          pairs={PAIRS}
          setups={SETUPS}
          sessions={SESSIONS}
        />
      )}
    </div>
  );
};

// Add Trade Modal Component
const AddTradeModal = ({ onClose, onSave, pairs, setups, sessions }) => {
  const [formData, setFormData] = useState({
    open_time: format(new Date(), 'yyyy-MM-dd HH:mm'),
    close_time: '',
    symbol: 'GBPUSD',
    trade_type: 'BUY',
    lots: 0.1,
    entry_price: '',
    exit_price: '',
    stop_loss: '',
    take_profit: '',
    pips: '',
    profit_loss: '',
    mae: '',
    r_value: '',
    trade_setup: 'Breakout',
    session: 'LONDON',
    duration_minutes: '',
    notes: '',
    screenshot_entry: '',
  });

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData({...formData, screenshot_entry: reader.result});
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:5000/api/journal/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to save entry');
      }
      
      if (data.success) {
        onSave();
        onClose();
      } else {
        throw new Error(data.message || 'Failed to save entry');
      }
    } catch (error) {
      console.error('Failed to save entry:', error);
      alert(`Failed to save entry: ${error.message}`);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gradient-green">Add Trade</h2>
            <button onClick={onClose} className="text-text-secondary hover:text-text-primary">
              <X size={24} />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Trade Details */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Open Time *</label>
                <input
                  type="datetime-local"
                  value={formData.open_time}
                  onChange={(e) => setFormData({...formData, open_time: e.target.value})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Symbol *</label>
                <select
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                  required
                >
                  {pairs.map(p => <option key={p} value={p} style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>{p}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Type *</label>
                <select
                  value={formData.trade_type}
                  onChange={(e) => setFormData({...formData, trade_type: e.target.value})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                  required
                >
                  <option value="BUY" style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>BUY</option>
                  <option value="SELL" style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>SELL</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Lots *</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.lots}
                  onChange={(e) => setFormData({...formData, lots: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Entry Price *</label>
                <input
                  type="number"
                  step="0.00001"
                  value={formData.entry_price}
                  onChange={(e) => setFormData({...formData, entry_price: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Exit Price</label>
                <input
                  type="number"
                  step="0.00001"
                  value={formData.exit_price}
                  onChange={(e) => setFormData({...formData, exit_price: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Stop Loss</label>
                <input
                  type="number"
                  step="0.00001"
                  value={formData.stop_loss}
                  onChange={(e) => setFormData({...formData, stop_loss: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Take Profit</label>
                <input
                  type="number"
                  step="0.00001"
                  value={formData.take_profit}
                  onChange={(e) => setFormData({...formData, take_profit: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Close Time</label>
                <input
                  type="datetime-local"
                  value={formData.close_time}
                  onChange={(e) => setFormData({...formData, close_time: e.target.value})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Pips</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.pips}
                  onChange={(e) => setFormData({...formData, pips: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">P/L ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.profit_loss}
                  onChange={(e) => setFormData({...formData, profit_loss: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">MAE</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.mae}
                  onChange={(e) => setFormData({...formData, mae: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">R-Value</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.r_value}
                  onChange={(e) => setFormData({...formData, r_value: parseFloat(e.target.value)})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Trade Setup</label>
                <select
                  value={formData.trade_setup}
                  onChange={(e) => setFormData({...formData, trade_setup: e.target.value})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                >
                  {setups.map(s => <option key={s} value={s} style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Session</label>
                <select
                  value={formData.session}
                  onChange={(e) => setFormData({...formData, session: e.target.value})}
                  className="w-full px-4 py-2.5 rounded-lg transition-all cursor-pointer"
                  style={{
                    backgroundColor: '#1A1F2E',
                    border: '1px solid #334155',
                    color: '#FFFFFF'
                  }}
                >
                  {sessions.map(s => <option key={s} value={s} style={{ backgroundColor: '#131825', color: '#FFFFFF' }}>{s}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="w-full px-4 py-2.5 rounded-lg transition-all resize-none"
                style={{
                  backgroundColor: '#1A1F2E',
                  border: '1px solid #334155',
                  color: '#FFFFFF'
                }}
                rows={3}
                placeholder="Trade analysis, lessons learned, etc..."
              />
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">Screenshot</label>
              <div className="flex items-center gap-4">
                <label className="btn-secondary cursor-pointer flex items-center gap-2">
                  <Upload size={18} />
                  Upload Image
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </label>
                {formData.screenshot_entry && (
                  <span className="text-green-500 text-sm flex items-center gap-2">
                    <Image size={16} />
                    Image uploaded
                  </span>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button type="button" onClick={onClose} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn-primary flex items-center gap-2">
                <Save size={18} />
                Save Trade
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Journal;
