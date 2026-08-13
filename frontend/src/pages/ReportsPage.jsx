import React, { useState } from 'react';
import { FileSpreadsheet, Download, Sparkles, CheckCircle2, FileText, Printer } from 'lucide-react';
import { useDocStore } from '../store/useDocStore';

export default function ReportsPage() {
  const { documents } = useDocStore();
  const [downloading, setDownloading] = useState(false);

  const handleExport = (type) => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      alert(`NexaDocs Intelligence Report exported successfully as ${type}!`);
    }, 800);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Intelligence Reports & Audit Export</h1>
          <p className="text-xs text-slate-500 mt-1">
            Generate executive PDFs, CSV topic matrices, and SOC2 compliance audit reports.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('CSV')}
            disabled={downloading}
            className="px-4 py-2 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl text-xs hover:bg-slate-50 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4 text-slate-500" />
            <span>Export CSV Data</span>
          </button>
          <button
            onClick={() => handleExport('PDF Executive Summary')}
            disabled={downloading}
            className="px-4 py-2 bg-blue-600 text-white font-bold rounded-xl text-xs hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all flex items-center gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Generate Executive PDF</span>
          </button>
        </div>
      </div>

      {/* Available Report Blueprints */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4 hover:border-blue-300 transition-all">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base">Q3 Financial Audit Summary</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Consolidated report covering $42.5M revenue, EBITDA growth (+31.2%), and audit findings.
          </p>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">38 Pages</span>
            <button onClick={() => handleExport('Financial PDF')} className="text-blue-600 font-bold hover:underline">
              Download PDF →
            </button>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4 hover:border-blue-300 transition-all">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Sparkles className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base">NexaDocs Technical Blueprint</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            FAISS vector benchmark specs, FastAPI backend architecture, and PyPDF parsing throughput.
          </p>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">22 Pages</span>
            <button onClick={() => handleExport('Technical Specs')} className="text-blue-600 font-bold hover:underline">
              Download PDF →
            </button>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4 hover:border-blue-300 transition-all">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <h3 className="font-bold text-slate-900 text-base">SOC2 Security SLA Audit</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Security policy verification, AES-256 cipher validation, and data retention compliance.
          </p>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">16 Pages</span>
            <button onClick={() => handleExport('SOC2 Audit Report')} className="text-blue-600 font-bold hover:underline">
              Download PDF →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
