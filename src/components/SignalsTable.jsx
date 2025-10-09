import React, { useMemo, useState } from 'react';

const headerDefs = [
  { key: 'time', label: 'Time' },
  { key: 'direction', label: 'Dir' },
  { key: 'entry', label: 'Entry' },
  { key: 'stop_loss', label: 'SL' },
  { key: 'tp1', label: 'TP1' },
  { key: 'tp2', label: 'TP2' },
  { key: 'confirmation_score', label: 'Conf' },
  { key: 'ml_probability', label: 'ML %' },
  { key: 'session', label: 'Session' }
];

const format = (value, key) => {
  if (value == null) return '-';
  if ([ 'entry', 'stop_loss', 'tp1', 'tp2' ].includes(key)) return Number(value).toFixed(5);
  if (key === 'ml_probability') return `${Math.round(Number(value) * 100)}%`;
  if (key === 'time') return new Date(value).toLocaleTimeString();
  return String(value);
};

const sortValue = (row, key) => {
  const v = row[key];
  if (v == null) return -Infinity;
  return typeof v === 'number' ? v : (key === 'time' ? new Date(v).getTime() : String(v));
};

const SignalsTable = ({ signals }) => {
  const [sortKey, setSortKey] = useState('time');
  const [sortDir, setSortDir] = useState('desc');

  const sorted = useMemo(() => {
    const arr = [...signals];
    arr.sort((a, b) => {
      const av = sortValue(a, sortKey);
      const bv = sortValue(b, sortKey);
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return arr;
  }, [signals, sortKey, sortDir]);

  const onSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  if (!signals || signals.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 text-center text-gray-400">
        No signals yet. Waiting for setup...
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-900">
            <tr>
              {headerDefs.map((h) => (
                <th
                  key={h.key}
                  className="px-3 py-2 text-left font-semibold text-gray-300 cursor-pointer select-none"
                  onClick={() => onSort(h.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{h.label}</span>
                    {sortKey === h.key && (
                      <span className="text-gray-500">{sortDir === 'asc' ? '▲' : '▼'}</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((s, idx) => (
              <tr key={idx} className="border-t border-gray-700 hover:bg-gray-750">
                {headerDefs.map((h) => (
                  <td key={h.key} className="px-3 py-2 whitespace-nowrap">
                    {h.key === 'direction' ? (
                      <span className={
                        s.direction === 'BUY' ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'
                      }>
                        {s.direction}
                      </span>
                    ) : (
                      <span className="text-gray-200">{format(s[h.key], h.key)}</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SignalsTable;



