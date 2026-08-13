import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Bot,
  Trash2,
  Download,
  Calendar,
  Layers,
  CheckCircle2,
  Clock,
  MoreVertical
} from 'lucide-react';
import { useDocStore } from '../store/useDocStore';

export default function DocumentCard({ doc, viewMode = 'grid' }) {
  const navigate = useNavigate();
  const { setActiveDoc, deleteDocument } = useDocStore();

  const handleOpenWorkspace = () => {
    setActiveDoc(doc);
    navigate('/app/workspace');
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${doc.filename}"?`)) {
      deleteDocument(doc.id);
    }
  };

  if (viewMode === 'list') {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-4 hover:border-slate-300 hover:shadow-subtle transition-all flex items-center justify-between gap-4">
        <div className="flex items-center gap-3.5 min-w-0 flex-1">
          <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-0.5">
              <h4
                onClick={handleOpenWorkspace}
                className="font-bold text-slate-900 text-sm truncate hover:text-blue-600 cursor-pointer transition-colors"
              >
                {doc.title}
              </h4>
              <span className="text-[10px] bg-slate-100 text-slate-700 font-semibold px-2 py-0.5 rounded-full shrink-0">
                {doc.category || 'General'}
              </span>
            </div>
            <p className="text-xs text-slate-500 truncate max-w-xl">
              {doc.summary}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 shrink-0">
          <div className="hidden sm:flex items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              {doc.pageCount} pgs ({doc.chunkCount} chunks)
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              {doc.createdAt}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleOpenWorkspace}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-100 rounded-lg text-xs font-semibold transition-colors"
            >
              <Bot className="w-3.5 h-3.5 text-blue-600" />
              <span>AI Chat</span>
            </button>

            <button
              onClick={handleDelete}
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Delete Document"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 hover:border-slate-300 hover:shadow-card-hover transition-all flex flex-col justify-between group">
      <div>
        {/* Card Header: Icon & Category */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] bg-slate-100 text-slate-700 font-medium px-2.5 py-0.5 rounded-full border border-slate-200/60">
              {doc.category || 'General'}
            </span>
            <span className="flex items-center gap-1 text-[11px] bg-emerald-50 text-emerald-700 font-semibold px-2 py-0.5 rounded-full border border-emerald-100">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              Ready
            </span>
          </div>
        </div>

        {/* Title */}
        <h4
          onClick={handleOpenWorkspace}
          className="font-bold text-slate-900 text-sm leading-snug line-clamp-2 mb-2 group-hover:text-blue-600 cursor-pointer transition-colors"
        >
          {doc.title}
        </h4>

        {/* Executive Summary */}
        <p className="text-xs text-slate-500 line-clamp-3 mb-4 leading-relaxed">
          {doc.summary}
        </p>

        {/* Key Topics Tags */}
        {doc.topics && doc.topics.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {doc.topics.slice(0, 3).map((topic, i) => (
              <span
                key={i}
                className="text-[10px] bg-slate-50 text-slate-600 font-medium px-2 py-0.5 rounded border border-slate-200/60"
              >
                #{topic}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Card Footer */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-3 text-[11px]">
          <span>{doc.pageCount} Pages</span>
          <span>•</span>
          <span>{doc.fileSize}</span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={handleOpenWorkspace}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white hover:bg-blue-700 rounded-lg text-xs font-semibold shadow-xs transition-all"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Open AI</span>
          </button>
          <button
            onClick={handleDelete}
            className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
            title="Delete Document"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
