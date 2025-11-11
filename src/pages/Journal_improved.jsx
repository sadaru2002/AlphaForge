import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { format } from 'date-fns';
import { Download, Plus, Trash2, FileDown, FileSpreadsheet, Image, X, Save, Upload } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import apiService from '../services/api';

const Journal = () => {
  const [rowData, setRowData] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
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

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this trade?')) return;
    
    try {
      await fetch(`http://localhost:5000/api/journal/entries/${id}`, {
        method: 'DELETE'
      });
      loadJournalEntries(); // Reload data
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
            className="input-field w-full"
          />
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">To</label>
          <input
            type="date"
            value={filters.to}
            onChange={(e) => setFilters({...filters, to: e.target.value})}
            className="input-field w-full"
          />
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Pair</label>
          <select
            value={filters.pair}
            onChange={(e) => setFilters({...filters, pair: e.target.value})}
            className="input-field w-full"
          >
            <option value="ALL">All Pairs</option>
            {PAIRS.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Setup</label>
          <select
            value={filters.setup}
            onChange={(e) => setFilters({...filters, setup: e.target.value})}
            className="input-field w-full"
          >
            <option value="ALL">All Setups</option>
            {SETUPS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Session</label>
          <select
            value={filters.session}
            onChange={(e) => setFilters({...filters, session: e.target.value})}
            className="input-field w-full"
          >
            <option value="ALL">All Sessions</option>
            {SESSIONS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

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
          onSave={loadJournalEntries}
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
      await fetch('http://localhost:5000/api/journal/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to save entry:', error);
      alert('Failed to save entry');
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
                  className="input-field w-full"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Symbol *</label>
                <select
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value})}
                  className="input-field w-full"
                  required
                >
                  {pairs.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Type *</label>
                <select
                  value={formData.trade_type}
                  onChange={(e) => setFormData({...formData, trade_type: e.target.value})}
                  className="input-field w-full"
                  required
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
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
                  className="input-field w-full"
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
                  className="input-field w-full"
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
                  className="input-field w-full"
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
                  className="input-field w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Take Profit</label>
                <input
                  type="number"
                  step="0.00001"
                  value={formData.take_profit}
                  onChange={(e) => setFormData({...formData, take_profit: parseFloat(e.target.value)})}
                  className="input-field w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Close Time</label>
                <input
                  type="datetime-local"
                  value={formData.close_time}
                  onChange={(e) => setFormData({...formData, close_time: e.target.value})}
                  className="input-field w-full"
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
                  className="input-field w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">P/L ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.profit_loss}
                  onChange={(e) => setFormData({...formData, profit_loss: parseFloat(e.target.value)})}
                  className="input-field w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">MAE</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.mae}
                  onChange={(e) => setFormData({...formData, mae: parseFloat(e.target.value)})}
                  className="input-field w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">R-Value</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.r_value}
                  onChange={(e) => setFormData({...formData, r_value: parseFloat(e.target.value)})}
                  className="input-field w-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-text-secondary mb-2">Trade Setup</label>
                <select
                  value={formData.trade_setup}
                  onChange={(e) => setFormData({...formData, trade_setup: e.target.value})}
                  className="input-field w-full"
                >
                  {setups.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-2">Session</label>
                <select
                  value={formData.session}
                  onChange={(e) => setFormData({...formData, session: e.target.value})}
                  className="input-field w-full"
                >
                  {sessions.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="input-field w-full"
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
