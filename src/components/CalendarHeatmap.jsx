import React, { useMemo } from 'react';
import { addDays, differenceInCalendarDays, eachWeekOfInterval, endOfMonth, endOfWeek, format, isSameMonth, parseISO, startOfMonth, startOfWeek } from 'date-fns';

// Simple calendar heatmap for daily P&L values
// Props:
// - values: Array<{ date: 'yyyy-MM-dd', value: number }>
// - from?: 'yyyy-MM-dd'
// - to?: 'yyyy-MM-dd'
const CalendarHeatmap = ({ values, from, to }) => {
  const valueByDate = useMemo(() => {
    const map = new Map();
    (values || []).forEach(({ date, value }) => {
      if (!date) return;
      const key = date.substring(0, 10);
      map.set(key, (map.get(key) || 0) + (Number(value) || 0));
    });
    return map;
  }, [values]);

  const { weeks, monthLabel } = useMemo(() => {
    const startDate = from ? parseISO(from) : startOfMonth(new Date());
    const endDate = to ? parseISO(to) : endOfMonth(new Date());
    const monthStart = startOfMonth(startDate);
    const monthEnd = endOfMonth(endDate);
    const calStart = startOfWeek(monthStart, { weekStartsOn: 0 });
    const calEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });

    const totalDays = Math.max(0, differenceInCalendarDays(calEnd, calStart) + 1);
    const days = Array.from({ length: totalDays }, (_, i) => addDays(calStart, i));

    let minV = 0;
    let maxV = 0;
    days.forEach(d => {
      const k = format(d, 'yyyy-MM-dd');
      const v = valueByDate.get(k) || 0;
      if (v < minV) minV = v;
      if (v > maxV) maxV = v;
    });

    const weekStarts = eachWeekOfInterval({ start: calStart, end: calEnd }, { weekStartsOn: 0 });
    const weeksArr = weekStarts.map(ws => Array.from({ length: 7 }, (_, i) => addDays(ws, i)));

    return { weeks: weeksArr, monthLabel: `${format(monthStart, 'MMM d')} - ${format(monthEnd, 'MMM d, yyyy')}` };
  }, [from, to, valueByDate]);

  const colorFor = (v) => {
    // Diverging scale: reds for negative, grays for zero, cyans for positive
    if (v === 0) return 'bg-slate-800 border-slate-700';
    if (v > 0) {
      // scale 1..5
      const s = v <= 50 ? 1 : v <= 150 ? 2 : v <= 300 ? 3 : v <= 600 ? 4 : 5;
      return [
        'bg-cyan-900/30 border-cyan-900/40',
        'bg-cyan-900/50 border-cyan-800/60',
        'bg-cyan-800/70 border-cyan-700/60',
        'bg-cyan-700/80 border-cyan-600/70',
        'bg-cyan-600/90 border-cyan-500/80'
      ][s - 1];
    }
    const nv = Math.abs(v);
    const s = nv <= 50 ? 1 : nv <= 150 ? 2 : nv <= 300 ? 3 : nv <= 600 ? 4 : 5;
    return [
      'bg-red-900/30 border-red-900/40',
      'bg-red-900/50 border-red-800/60',
      'bg-red-800/70 border-red-700/60',
      'bg-red-700/80 border-red-600/70',
      'bg-red-600/90 border-red-500/80'
    ][s - 1];
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="font-semibold">P&L Calendar</div>
        <div className="text-xs text-gray-400">{monthLabel}</div>
      </div>
      <div className="flex">
        {/* Weekday labels */}
        <div className="mr-2 text-[10px] text-gray-400 grid grid-rows-7 gap-1 py-1">
          {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(d => (
            <div key={d} className="h-6 flex items-center">{d}</div>
          ))}
        </div>
        <div className="overflow-x-auto">
          <div className="grid" style={{ gridTemplateColumns: `repeat(${weeks.length}, 1fr)` }}>
            {weeks.map((week, wi) => (
              <div key={wi} className="grid grid-rows-7 gap-1 px-0.5">
                {week.map((day, di) => {
                  const key = format(day, 'yyyy-MM-dd');
                  const v = valueByDate.get(key) || 0;
                  const inMonth = isSameMonth(day, from ? parseISO(from) : new Date()) || isSameMonth(day, to ? parseISO(to) : new Date());
                  const cellBase = `h-6 w-6 rounded-sm border ${colorFor(v)} ${inMonth ? '' : 'opacity-40'}`;
                  return (
                    <div key={di} className="relative group">
                      <div className={cellBase} title={`${key}: ${v >= 0 ? '+' : ''}${v}`}></div>
                      <div className="pointer-events-none absolute left-7 top-1/2 -translate-y-1/2 whitespace-nowrap rounded bg-gray-900 border border-gray-700 px-2 py-1 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity z-10">
                        {format(day, 'MMM d')}: {v >= 0 ? '+' : ''}{v}
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Legend */}
      <div className="flex items-center justify-end mt-3 text-[10px] text-gray-400 space-x-2">
        <span>Loss</span>
        <div className="h-3 w-3 rounded-sm bg-red-900/30 border border-red-900/40" />
        <div className="h-3 w-3 rounded-sm bg-red-700/80 border border-red-600/70" />
        <div className="h-3 w-3 rounded-sm bg-red-600/90 border border-red-500/80" />
        <span className="mx-1">|</span>
        <div className="h-3 w-3 rounded-sm bg-cyan-600/90 border border-cyan-500/80" />
        <div className="h-3 w-3 rounded-sm bg-cyan-700/80 border border-cyan-600/70" />
        <div className="h-3 w-3 rounded-sm bg-cyan-900/30 border border-cyan-900/40" />
        <span>Gain</span>
      </div>
    </div>
  );
};

export default CalendarHeatmap;


