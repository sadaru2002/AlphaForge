import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { format } from 'date-fns';
import { Download, Plus, Filter, FileDown, FileSpreadsheet, Calendar, PieChart, BarChart2, LineChart } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import JournalDetailsPanel from './JournalDetailsPanel';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import CalendarHeatmap from '../components/CalendarHeatmap';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend);

const darkCard = 'bg-[#1A1F35] border border-[#2A2F45]';

const Journal = () => {
  // const [range, setRange] = useState([{ startDate: new Date(), endDate: new Date(), key: 'selection' }]);
  // eslint-disable-next-line no-unused-vars
  import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { format } from 'date-fns';
import { 
  Download, Plus, Filter, FileDown, FileSpreadsheet, Calendar, 
  PieChart, BarChart2, LineChart, TrendingUp, TrendingDown, 
  Target, Award, Activity, DollarSign, Percent, Clock, 
  AlertTriangle, CheckCircle, XCircle, Image as ImageIcon, 
  Edit3, Save, X, Users, Zap
} from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import JournalDetailsPanel from './JournalDetailsPanel';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import CalendarHeatmap from '../components/CalendarHeatmap';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend, RadialLinearScale } from 'chart.js';
import * as xlsx from 'xlsx';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend, RadialLinearScale);

const darkCard = 'bg-main border border-line';

const Journal = () => {
  const gridRef = useRef(null);
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [quick, setQuick] = useState('Last 7 Days');
  const [rowData, setRowData] = useState([]);
  const [filters, setFilters] = useState({
    pair: 'ALL',
    setup: 'ALL',
    session: 'ALL',
    from: format(new Date(), 'yyyy-MM-01'),
    to: format(new Date(), 'yyyy-MM-dd')
  });
  const gridRef = useRef(null);

  const columnDefs = useMemo(() => ([
    { headerName: 'Open Time', field: 'openTime', sortable: true, filter: 'agDateColumnFilter', editable: true },
    { headerName: 'Type', field: 'type', sortable: true, filter: true, editable: true },
    { headerName: 'Lots', field: 'lots', sortable: true, filter: true, editable: true },
    { headerName: 'Symbol', field: 'symbol', sortable: true, filter: true, editable: true },
    { headerName: 'Entry Price', field: 'entry', sortable: true, filter: true, editable: true },
    { headerName: 'S/L', field: 'sl', sortable: true, filter: true, editable: true },
    { headerName: 'T/P', field: 'tp', sortable: true, filter: true, editable: true },
    { headerName: 'Close Time', field: 'closeTime', sortable: true, filter: 'agDateColumnFilter', editable: true },
    { headerName: 'Exit Price', field: 'exit', sortable: true, filter: true, editable: true },
    { headerName: 'Total Pips', field: 'pips', sortable: true, filter: true, editable: true },
    { headerName: 'P/L', field: 'pl', sortable: true, filter: true, editable: true },
    { headerName: 'MAE', field: 'mae', sortable: true, filter: true, editable: true },
    { headerName: 'Duration', field: 'duration', sortable: true, filter: true, editable: true },
    { headerName: 'R-Value', field: 'r', sortable: true, filter: true, editable: true },
    { headerName: 'Trade Setup', field: 'setup', sortable: true, filter: true, editable: true },
  ]), []);

  const defaultColDef = useMemo(() => ({ resizable: true, minWidth: 110, suppressHeaderMenuButton: true }), []);

  // Demo seed data (replace with backend data when available)
  useEffect(() => {
    if (!rowData || rowData.length === 0) {
      setRowData([
        { openTime: '2025-10-01 09:05', type: 'BUY', lots: 0.2, symbol: 'GBPUSD', entry: 1.26850, sl: 1.26750, tp: 1.27150, closeTime: '2025-10-01 10:10', exit: 1.27070, pips: 22, pl: 220, mae: -6, duration: '1h 5m', r: 2.2, setup: 'Trend Continuation' },
        { openTime: '2025-10-02 13:20', type: 'SELL', lots: 0.1, symbol: 'EURUSD', entry: 1.07840, sl: 1.07900, tp: 1.07600, closeTime: '2025-10-02 14:10', exit: 1.07910, pips: -7, pl: -70, mae: -2, duration: '50m', r: -0.7, setup: 'Breakout Failure' },
        { openTime: '2025-10-03 08:15', type: 'BUY', lots: 0.15, symbol: 'GBPUSD', entry: 1.27010, sl: 1.26900, tp: 1.27310, closeTime: '2025-10-03 09:00', exit: 1.27260, pips: 25, pl: 250, mae: -4, duration: '45m', r: 2.5, setup: 'Smart Money Setup' },
      ]);
    }
  }, [rowData]);

  const filteredRowData = useMemo(() => {
    return rowData.filter((r) => {
      const d = r.openTime ? r.openTime.split(' ')[0] : '';
      const inDate = (!filters.from || d >= filters.from) && (!filters.to || d <= filters.to);
      const byPair = filters.pair === 'ALL' || r.symbol === filters.pair;
      const bySetup = filters.setup === 'ALL' || r.setup === filters.setup;
      const bySession = filters.session === 'ALL' || true; // placeholder until session is stored per trade
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
    const headers = ['Open Time','Type','Lots','Symbol','Entry Price','S/L','T/P','Close Time','Exit Price','Total Pips','Profit/Loss','MAE','Duration','R-Value','Trade Setup'];
    const lines = [headers.join(',')];
    filteredRowData.forEach((r) => {
      const row = [r.openTime,r.type,r.lots,r.symbol,r.entry,r.sl,r.tp,r.closeTime,r.exit,r.pips,r.pl,r.mae,r.duration,r.r,r.setup]
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

  const onExportPDF = async () => {
    const doc = new jsPDF({ orientation: 'landscape' });
    doc.setFontSize(14);
    doc.text('AlphaForge Trading Journal', 14, 16);
    const rows = filteredRowData.map((r) => [r.openTime, r.type, r.lots, r.symbol, r.entry, r.sl, r.tp, r.closeTime, r.exit, r.pips, r.pl, r.mae, r.duration, r.r, r.setup]);
    doc.autoTable({
      head: [['Open Time','Type','Lots','Symbol','Entry','S/L','T/P','Close Time','Exit','Pips','P/L','MAE','Duration','R','Setup']],
      body: rows,
      styles: { fontSize: 8 },
      startY: 22,
    });
    doc.save(`journal-${filters.from}-${filters.to}.pdf`);
  };

  const onAddTrade = () => {
    const newRow = { openTime: format(new Date(), 'yyyy-MM-dd HH:mm'), type: 'BUY', lots: 0.1, symbol: 'GBPUSD', entry: 1.27000, sl: 1.26900, tp: 1.27300, closeTime: '', exit: '', pips: '', pl: '', mae: '', duration: '', r: '', setup: 'Manual' };
    setRowData((prev) => [newRow, ...prev]);
  };

  const lineData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    datasets: [
      {
        label: 'Cumulative Balance',
        data: [10000, 10050, 10010, 10120, 10180],
        fill: true,
        backgroundColor: 'rgba(6, 182, 212, 0.15)',
        borderColor: 'rgba(6, 182, 212, 1)'
      }
    ]
  };

  const barData = {
    labels: ['2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04', '2025-10-05'],
    datasets: [
      { label: 'Gains', data: [200, 0, 150, 0, 120], backgroundColor: '#06B6D4' },
      { label: 'Losses', data: [0, -80, 0, -60, 0], backgroundColor: '#EF4444' }
    ]
  };

  const donutWins = {
    labels: ['Wins', 'Losses', 'BE'],
    datasets: [{ data: [18, 7, 2], backgroundColor: ['#06B6D4', '#EF4444', '#334155'] }]
  };

  const heatValues = useMemo(() => {
    const map = new Map();
    filteredRowData.forEach((r) => {
      const d = r.openTime ? r.openTime.substring(0, 10) : undefined;
      if (!d) return;
      const cur = map.get(d) || 0;
      map.set(d, cur + (Number(r.pl) || 0));
    });
    return Array.from(map.entries()).map(([date, value]) => ({ date, value }));
  }, [filteredRowData]);

  return (
    <div className="min-h-screen bg-[#0F1419] text-[#E5E7EB] flex flex-col">
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6 flex-1 flex flex-col min-h-0">
        {/* Tabs */}
        <div className="mb-6 flex flex-wrap items-center space-x-3 text-sm">
          {['Dashboard', 'Trade Log', 'Analytics', 'Calendar', 'Backtesting', 'Reports'].map((t) => (
            <span key={t} className={`px-3 py-1.5 rounded-full border ${t === 'Trade Log' ? 'bg-[#1E2139] border-[#2A2F45] text-white' : 'border-[#2A2F45] text-gray-300 hover:text-white'}`}>{t}</span>
          ))}
        </div>

        {/* Metrics + Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}> 
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-400">Current Balance</div>
                <div className="text-3xl font-bold">$10,180</div>
                <div className="text-xs text-cyan-400 mt-1">+1.8% MoM</div>
              </div>
              <div className="w-12 h-12 rounded-full border-4 border-cyan-500 flex items-center justify-center">82%</div>
            </div>
          </div>
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}> 
            <div className="text-xs text-gray-400">Net P/L (Monthly)</div>
            <div className="text-3xl font-bold text-cyan-400">+$420</div>
            <div className="text-xs mt-1">▲ vs last month</div>
          </div>
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}> 
            <div className="text-xs text-gray-400">Win Rate</div>
            <div className="text-3xl font-bold">72%</div>
            <div className="text-xs text-gray-400 mt-1">Cumulative</div>
          </div>
        </div>

        {/* Controls */}
        <div className={`${darkCard} rounded-xl p-4 shadow-sm mb-6 flex flex-wrap items-center justify-between`}>
          <div className="flex items-center space-x-2 text-sm">
            <button className="px-3 py-2 bg-[#1E2139] border border-[#2A2F45] rounded flex items-center space-x-2"><Filter size={16}/><span>Filters</span></button>
            <button className="px-3 py-2 bg-[#1E2139] border border-[#2A2F45] rounded flex items-center space-x-2"><Calendar size={16}/><span>{quick}</span></button>
            <input type="date" className="bg-[#1E2139] border border-[#2A2F45] rounded px-2 py-1" value={filters.from} onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value }))} />
            <span className="text-gray-500">→</span>
            <input type="date" className="bg-[#1E2139] border border-[#2A2F45] rounded px-2 py-1" value={filters.to} onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value }))} />
            <select className="bg-[#1E2139] border border-[#2A2F45] rounded px-2 py-1" value={filters.pair} onChange={(e) => setFilters((f) => ({ ...f, pair: e.target.value }))}>
              <option value="ALL">All Pairs</option>
              <option value="GBPUSD">GBPUSD</option>
              <option value="EURUSD">EURUSD</option>
              <option value="AUDUSD">AUDUSD</option>
            </select>
            <select className="bg-[#1E2139] border border-[#2A2F45] rounded px-2 py-1" value={filters.setup} onChange={(e) => setFilters((f) => ({ ...f, setup: e.target.value }))}>
              <option value="ALL">All Setups</option>
              <option>Trend Continuation</option>
              <option>Breakout Failure</option>
              <option>Smart Money Setup</option>
              <option>Structure Break</option>
            </select>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <button onClick={onExportCSV} className="px-3 py-2 bg-[#1E2139] border border-[#2A2F45] rounded flex items-center space-x-2"><FileSpreadsheet size={16}/><span>CSV</span></button>
            <button onClick={onExportPDF} className="px-3 py-2 bg-[#1E2139] border border-[#2A2F45] rounded flex items-center space-x-2"><FileDown size={16}/><span>PDF</span></button>
            <button onClick={onExportExcel} className="px-3 py-2 bg-[#1E2139] border border-[#2A2F45] rounded flex items-center space-x-2"><Download size={16}/><span>Excel</span></button>
          </div>
        </div>

        {/* Trade Table */}
        <div className={`${darkCard} rounded-xl p-2 shadow-sm mb-6 flex-1 min-h-0`}> 
          <div className="ag-theme-alpine h-[40vh] md:h-[45vh] lg:h-[50vh] w-full">
            <AgGridReact
              ref={gridRef}
              rowData={filteredRowData}
              columnDefs={columnDefs}
              defaultColDef={defaultColDef}
              pagination={true}
              paginationPageSize={25}
              rowClassRules={{
                'bg-green-950/40': (p) => Number(p.data?.pl) > 0,
                'bg-red-950/40': (p) => Number(p.data?.pl) < 0,
              }}
            />
          </div>
        </div>

        {/* Analytics Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}>
            <div className="flex items-center justify-between mb-3"><span className="font-semibold">Distribution of Gains & Losses</span><BarChart2 size={16}/></div>
            <div className="h-64 md:h-80">
              <Bar data={barData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#E5E7EB' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }} />
            </div>
          </div>
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}>
            <div className="flex items-center justify-between mb-3"><span className="font-semibold">Wins & Losses</span><PieChart size={16}/></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="h-60">
                <Doughnut data={donutWins} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#E5E7EB' } } } }} />
              </div>
              <div className="h-60">
                <Doughnut data={donutWins} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#E5E7EB' } } } }} />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}>
            <div className="flex items-center justify-between mb-3"><span className="font-semibold">Performance Curve</span><LineChart size={16}/></div>
            <div className="flex items-center space-x-2 text-xs mb-2">
              {['Daily', 'Weekly', 'Monthly', 'All'].map((f) => (
                <span key={f} className={`px-2 py-1 rounded border ${f === 'Daily' ? 'bg-[#1E2139] border-[#2A2F45]' : 'border-[#2A2F45]'}`}>{f}</span>
              ))}
            </div>
            <div className="h-64 md:h-80">
              <Line data={lineData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#E5E7EB' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }} />
            </div>
          </div>
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}>
            <div className="flex items-center justify-between mb-3"><span className="font-semibold">Weekly Performance</span><BarChart2 size={16}/></div>
            <div className="h-64 md:h-80">
              <Bar data={{ labels: ['This Week', 'Last Week'], datasets: [{ label: 'P/L', data: [320, 190], backgroundColor: ['#06B6D4', '#EF4444'] }] }} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#E5E7EB' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }} />
            </div>
          </div>
        </div>

        {/* Calendar Heatmap */}
        <div className={`${darkCard} rounded-xl p-4 shadow-sm mt-4 heatmap-sm`}>
          <div className="overflow-x-auto">
            <CalendarHeatmap values={heatValues} from={filters.from} to={filters.to} />
          </div>
        </div>

        {/* Details Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}>
            <div className="font-semibold mb-3">Selected Trade Details</div>
            <JournalDetailsPanel
              trade={filteredRowData[0]}
              onChange={(updated) => {
                setRowData((prev) => {
                  const idx = prev.findIndex((r) => r.openTime === updated.openTime && r.symbol === updated.symbol);
                  if (idx === -1) return prev;
                  const next = [...prev];
                  next[idx] = updated;
                  return next;
                });
              }}
              onAttachScreenshot={(file) => {
                if (!file) return;
                const reader = new FileReader();
                reader.onload = () => {
                  setRowData((prev) => {
                    if (prev.length === 0) return prev;
                    const next = [...prev];
                    next[0] = { ...next[0], screenshot: reader.result };
                    return next;
                  });
                };
                reader.readAsDataURL(file);
              }}
            />
          </div>
          <div className={`${darkCard} rounded-xl p-4 shadow-sm`}>
            <div className="font-semibold mb-3">Quick Stats</div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-[#1E2139] border border-[#2A2F45] rounded p-3">Long Net P&L<br/><span className="text-cyan-400 font-semibold">$540</span></div>
              <div className="bg-[#1E2139] border border-[#2A2F45] rounded p-3">Short Net P&L<br/><span className="text-cyan-400 font-semibold">$260</span></div>
              <div className="bg-[#1E2139] border border-[#2A2F45] rounded p-3">Profit Factor<br/><span className="font-semibold">2.1</span></div>
              <div className="bg-[#1E2139] border border-[#2A2F45] rounded p-3">Trades (M/M)<br/><span className="font-semibold">27</span></div>
            </div>
          </div>
        </div>

        {/* FAB */}
        <button onClick={onAddTrade} className="fixed bottom-6 right-6 bg-cyan-600 hover:bg-cyan-500 text-white rounded-full p-4 shadow-lg flex items-center space-x-2">
          <Plus size={18} />
          <span className="hidden md:inline text-sm">Add Trade</span>
        </button>
      </div>
    </div>
  );
};

export default Journal;
