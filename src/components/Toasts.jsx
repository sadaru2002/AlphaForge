import React, { useEffect } from 'react';

const Toasts = ({ toasts, remove }) => {
  useEffect(() => {
    const timers = toasts.map((t) => setTimeout(() => remove(t.id), t.ttl || 3500));
    return () => timers.forEach(clearTimeout);
  }, [toasts, remove]);

  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 space-y-2 z-50">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`px-4 py-3 rounded shadow border ${
            t.type === 'error' ? 'bg-red-900/80 border-red-700 text-red-100' :
            t.type === 'success' ? 'bg-green-900/80 border-green-700 text-green-100' :
            'bg-gray-800/80 border-gray-700 text-gray-100'
          }`}
        >
          <div className="font-semibold">{t.title || (t.type === 'error' ? 'Error' : 'Notice')}</div>
          {t.message && <div className="text-sm mt-0.5 opacity-90">{t.message}</div>}
        </div>
      ))}
    </div>
  );
};

export default Toasts;







