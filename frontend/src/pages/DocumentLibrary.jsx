import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Search,
  UploadCloud,
  Grid,
  List,
  Filter,
  Layers,
  FolderOpen,
  Plus,
  Trash2,
  Sparkles
} from 'lucide-react';
import { useDocStore } from '../store/useDocStore';
import DocumentCard from '../components/DocumentCard';
import UploadModal from '../components/UploadModal';

export default function DocumentLibrary() {
  const [viewMode, setViewMode] = useState('grid');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const navigate = useNavigate();

  const {
    searchQuery,
    setSearchQuery,
    categoryFilter,
    setCategoryFilter,
    getFilteredDocuments,
    documents,
    fetchDocuments
  } = useDocStore();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const filteredDocs = getFilteredDocuments();
  const categories = ['All', 'Finance', 'Engineering', 'Legal & Compliance', 'Research'];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Page Title & Main Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Document Library</h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage, filter, and inspect vector-indexed PDF documents in your knowledge base.
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all flex items-center justify-center gap-2"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload PDF Document</span>
        </button>
      </div>

      {/* Filter Bar & Controls */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Search Box */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search document title, filename, or summary..."
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
            />
          </div>

          {/* View Switcher Controls */}
          <div className="flex items-center gap-2 justify-end">
            <span className="text-xs text-slate-500 font-medium mr-2">
              Showing {filteredDocs.length} of {documents.length} files
            </span>

            <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg transition-colors ${
                  viewMode === 'grid' ? 'bg-white text-blue-600 shadow-2xs font-bold' : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Grid View"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded-lg transition-colors ${
                  viewMode === 'list' ? 'bg-white text-blue-600 shadow-2xs font-bold' : 'text-slate-500 hover:text-slate-800'
                }`}
                title="List View"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Category Pill Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0 mr-1" />
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                categoryFilter === cat
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-slate-50 text-slate-600 border border-slate-200/80 hover:bg-slate-100'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Document Grid / List Output */}
      {filteredDocs.length > 0 ? (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-3'
          }
        >
          {filteredDocs.map((doc) => (
            <DocumentCard key={doc.id} doc={doc} viewMode={viewMode} />
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-slate-50 text-slate-400 border border-slate-200 flex items-center justify-center mx-auto">
            <FolderOpen className="w-8 h-8" />
          </div>
          <div className="max-w-sm mx-auto space-y-1">
            <h3 className="font-bold text-slate-900 text-base">No Documents Found</h3>
            <p className="text-xs text-slate-500">
              No matching PDF documents found for "{searchQuery || categoryFilter}". Try clearing your filters or uploading a new file.
            </p>
          </div>
          <button
            onClick={() => {
              setSearchQuery('');
              setCategoryFilter('All');
            }}
            className="px-4 py-2 bg-slate-100 text-slate-700 font-semibold rounded-xl text-xs hover:bg-slate-200 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      )}

      <UploadModal isOpen={showUploadModal} onClose={() => setShowUploadModal(false)} />
    </div>
  );
}
