import React from 'react';
import { LineChart, Sparkles, Tag, Building, FileText, CheckCircle2, TrendingUp } from 'lucide-react';
import { useDocStore } from '../store/useDocStore';

export default function InsightsPage() {
  const { documents } = useDocStore();

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Cross-Document Insights & Analytics</h1>
        <p className="text-xs text-slate-500 mt-1">
          Automated topic clusters, monetary metric aggregations, and entity extractions across your entire document base.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-2">
          <span className="text-xs font-semibold text-slate-500">Extracted Topics</span>
          <p className="text-3xl font-extrabold text-slate-900">24 Clusters</p>
          <p className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> High semantic cohesion
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-2">
          <span className="text-xs font-semibold text-slate-500">Key Entities Identified</span>
          <p className="text-3xl font-extrabold text-slate-900">86 Entities</p>
          <p className="text-[11px] text-blue-600 font-semibold">Orgs, Financials, Dates & SLAs</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-2">
          <span className="text-xs font-semibold text-slate-500">Vector Confidence Score</span>
          <p className="text-3xl font-extrabold text-slate-900">98.4%</p>
          <p className="text-[11px] text-slate-400">FAISS k-NN vector precision</p>
        </div>
      </div>

      {/* Detailed Insights Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Document Topic Map */}
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Tag className="w-4 h-4 text-blue-600" />
            Top Extracted Topic Clusters
          </h3>

          <div className="space-y-3">
            {[
              { topic: 'Revenue Optimization & Margins', count: '142 chunks', pct: 88 },
              { topic: 'FAISS & FastAPI System Blueprint', count: '88 chunks', pct: 65 },
              { topic: 'SOC2 Privacy & Security SLA', count: '54 chunks', pct: 42 },
              { topic: 'Healthcare RAG Clinical Study', count: '210 chunks', pct: 94 }
            ].map((t, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold text-slate-800">
                  <span>{t.topic}</span>
                  <span className="text-slate-500">{t.count}</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 rounded-full" style={{ width: `${t.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Global Entities Breakdown */}
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Building className="w-4 h-4 text-blue-600" />
            Global Organizations & Metrics Extracted
          </h3>

          <div className="space-y-2.5 text-xs">
            {documents.flatMap(d => d.entities || []).slice(0, 5).map((ent, i) => (
              <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                <div>
                  <span className="font-bold text-slate-900 block">{ent.name}</span>
                  <span className="text-[10px] text-slate-400 font-medium">{ent.type}</span>
                </div>
                <span className="text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-100 px-2.5 py-1 rounded-lg">
                  {ent.detail}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
