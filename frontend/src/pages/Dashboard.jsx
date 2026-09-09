import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Bot,
  HardDrive,
  Sparkles,
  TrendingUp,
  Clock,
  ArrowRight,
  Plus,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Zap,
  Activity,
  Loader2
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { useAuthStore } from '../store/useAuthStore';
import { useDocStore } from '../store/useDocStore';
import DocumentCard from '../components/DocumentCard';
import UploadModal from '../components/UploadModal';

const ACTIVITY_DATA = [
  { day: 'Mon', uploads: 4, aiQueries: 18 },
  { day: 'Tue', uploads: 8, aiQueries: 32 },
  { day: 'Wed', uploads: 5, aiQueries: 24 },
  { day: 'Thu', uploads: 12, aiQueries: 48 },
  { day: 'Fri', uploads: 9, aiQueries: 38 },
  { day: 'Sat', uploads: 3, aiQueries: 14 },
  { day: 'Sun', uploads: 6, aiQueries: 22 },
];

export default function Dashboard() {
  const { user } = useAuthStore();
  const { documents, setActiveDoc, isUploading, uploadProgress, fetchDocuments } = useDocStore();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const totalPages = documents.reduce((sum, d) => sum + (d.pageCount || 0), 0);
  const totalChunks = documents.reduce((sum, d) => sum + (d.chunkCount || 0), 0);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-3xl p-6 sm:p-8 text-white shadow-lg shadow-blue-500/15 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-white text-xs font-semibold backdrop-blur-xs">
            <Sparkles className="w-3.5 h-3.5 text-blue-200" />
            <span>NexaDocs FAISS Vector Engine Active</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.name || 'Sarah'}!
          </h1>
          <p className="text-blue-100 text-xs sm:text-sm max-w-xl font-normal">
            Your document intelligence pipeline has processed {documents.length} PDF files with {totalChunks} vector chunks. Explore insights or launch a RAG conversation below.
          </p>
        </div>

        <div className="flex items-center gap-3 relative z-10">
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2.5 bg-white text-blue-700 font-bold rounded-xl text-xs hover:bg-blue-50 shadow-md transition-all flex items-center gap-2"
          >
            <Plus className="w-4 h-4 text-blue-600" />
            <span>Upload New PDF</span>
          </button>

          <button
            onClick={() => navigate('/app/workspace')}
            className="px-4 py-2.5 bg-blue-800/60 text-white font-semibold rounded-xl text-xs hover:bg-blue-800 border border-blue-400/30 backdrop-blur-xs transition-all flex items-center gap-2"
          >
            <Bot className="w-4 h-4 text-blue-200" />
            <span>Open AI Workspace</span>
          </button>
        </div>
      </div>

      {/* Active Processing Card Banner (if uploading) */}
      {isUploading && (
        <div className="bg-white border-2 border-blue-600 rounded-2xl p-5 shadow-md flex items-center justify-between gap-4 animate-pulse">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-sm">Processing Document Knowledge Index...</h4>
              <p className="text-xs text-slate-500">Executing PDF text extraction, chunking & FAISS embeddings</p>
            </div>
          </div>
          <div className="text-right min-w-[120px]">
            <span className="text-sm font-extrabold text-blue-600">{uploadProgress}% Complete</span>
            <div className="w-32 h-2 bg-slate-100 rounded-full mt-1 overflow-hidden">
              <div className="h-full bg-blue-600 rounded-full transition-all duration-300" style={{ width: `${uploadProgress}%` }} />
            </div>
          </div>
        </div>
      )}

      {/* 4 Statistics Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-subtle transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500">Documents Processed</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900">{documents.length}</span>
            <span className="text-[11px] font-semibold text-emerald-600 flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> +2 this week
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{totalPages} total pages parsed</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-subtle transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500">Questions Answered</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900">196</span>
            <span className="text-[11px] font-semibold text-emerald-600 flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> 98.4% precision
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{totalChunks} FAISS vector embeddings</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-subtle transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500">Storage Usage</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <HardDrive className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900">
              {user?.storageUsed || 1.42} GB
            </span>
            <span className="text-[11px] font-semibold text-slate-500">
              of {user?.storageLimit || 10} GB
            </span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full mt-2 overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full"
              style={{ width: `${((user?.storageUsed || 1.42) / (user?.storageLimit || 10)) * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-subtle transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500">AI Insights Generated</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-slate-900">86</span>
            <span className="text-[11px] font-semibold text-emerald-600 font-medium">Entities & Summaries</span>
          </div>
          <p className="text-[11px] text-emerald-600 font-medium mt-1 flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-500" /> RAG Latency &lt; 180ms
          </p>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Weekly Document Activity Bar Chart */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-blue-600" />
                Weekly Document & Query Activity
              </h3>
              <p className="text-xs text-slate-500">Upload volume vs. RAG AI queries processed per day</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ACTIVITY_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Bar dataKey="uploads" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Uploads" />
                <Bar dataKey="aiQueries" fill="#2563EB" radius={[4, 4, 0, 0]} name="AI Queries" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Usage History Area Chart */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
          <div>
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              AI Vector Token Usage Trend
            </h3>
            <p className="text-xs text-slate-500">Context token consumption trajectory</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={ACTIVITY_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderRadius: '8px', color: '#fff', fontSize: '11px' }} />
                <Area type="monotone" dataKey="aiQueries" stroke="#2563EB" strokeWidth={2} fillOpacity={1} fill="url(#colorQueries)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Documents Table & Activity */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Recent Knowledge Base Documents</h3>
            <p className="text-xs text-slate-500">Active PDF documents in vector storage</p>
          </div>
          <button
            onClick={() => navigate('/app/documents')}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            <span>View All ({documents.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.slice(0, 3).map((doc) => (
            <DocumentCard key={doc.id} doc={doc} viewMode="grid" />
          ))}
        </div>
      </div>

      <UploadModal isOpen={showUploadModal} onClose={() => setShowUploadModal(false)} />
    </div>
  );
}
