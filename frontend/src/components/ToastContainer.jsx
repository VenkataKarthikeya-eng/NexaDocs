import React from 'react';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';
import { useToastStore } from '../store/useToastStore';

export default function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((t) => {
        let bgClass = 'bg-slate-900 text-white border-slate-800';
        let Icon = Info;

        if (t.type === 'success') {
          bgClass = 'bg-emerald-600 text-white border-emerald-500 shadow-emerald-500/20';
          Icon = CheckCircle2;
        } else if (t.type === 'error') {
          bgClass = 'bg-red-600 text-white border-red-500 shadow-red-500/20';
          Icon = AlertCircle;
        } else if (t.type === 'warning') {
          bgClass = 'bg-amber-600 text-white border-amber-500 shadow-amber-500/20';
          Icon = AlertTriangle;
        }

        return (
          <div
            key={t.id}
            className={`flex items-center justify-between p-3.5 rounded-xl border shadow-lg text-xs font-semibold animate-in slide-in-from-bottom-2 duration-200 ${bgClass}`}
          >
            <div className="flex items-center gap-2.5 min-w-0 pr-2">
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{t.message}</span>
            </div>
            <button
              onClick={() => removeToast(t.id)}
              className="p-1 rounded hover:bg-white/20 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
