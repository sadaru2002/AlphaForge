import React, { useEffect } from 'react';

const Toasts = ({ toasts, remove }) => {
  return (
    <div className="fixed top-20 right-6 z-50 space-y-3">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={() => remove(toast.id)} />
      ))}
    </div>
  );
};

const Toast = ({ toast, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const getToastStyles = () => {
    switch (toast.type) {
      case 'success':
        return 'bg-green-500/10 border-green-500 text-green-400';
      case 'error':
        return 'bg-red-500/10 border-red-500 text-red-400';
      case 'warning':
        return 'bg-yellow-500/10 border-yellow-500 text-yellow-400';
      default:
        return 'bg-blue-500/10 border-blue-500 text-blue-400';
    }
  };

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className={`flex items-start gap-3 min-w-80 max-w-md p-4 rounded-lg border ${getToastStyles()} transition-smooth shadow-lg`}>
      <span className="text-2xl">{getIcon()}</span>
      <div className="flex-1">
        <h4 className="font-semibold mb-1">{toast.title}</h4>
        <p className="text-small opacity-90">{toast.message}</p>
      </div>
      <button onClick={onClose} className="text-lg opacity-70 hover:opacity-100">×</button>
    </div>
  );
};

export default Toasts;
