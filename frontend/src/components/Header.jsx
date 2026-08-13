import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  UploadCloud,
  Bell,
  Menu,
  Sparkles,
  Command,
  HelpCircle,
  FilePlus,
  CheckCircle2
} from 'lucide-react';
import { useDocStore } from '../store/useDocStore';
import UploadModal from './UploadModal';

export default function Header({ setMobileOpen }) {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const { searchQuery, setSearchQuery } = useDocStore();
  const navigate = useNavigate();

  return (
    <>
      <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-30 px-4 sm:px-6 flex items-center justify-between shadow-xs">
        {/* Left: Mobile Toggle & Global Search */}
        <div className="flex items-center gap-3 flex-1 max-w-xl">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 text-slate-600 rounded-lg lg:hidden hover:bg-slate-100"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents, vector chunks, or key topics... (Ctrl+K)"
              className="w-full pl-9 pr-12 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
            />
            <kbd className="hidden sm:flex items-center gap-0.5 absolute right-3 top-1/2 -translate-y-1/2 bg-white border border-slate-200 px-1.5 py-0.5 rounded text-[10px] text-slate-400 font-medium shadow-2xs">
              <Command className="w-3 h-3" /> K
            </kbd>
          </div>
        </div>

        {/* Right Action Trigger Buttons */}
        <div className="flex items-center gap-3">
          {/* Quick AI Workspace Shortcut */}
          <button
            onClick={() => navigate('/app/workspace')}
            className="hidden md:flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-700 border border-blue-100 rounded-lg text-xs font-semibold hover:bg-blue-100 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>AI Workspace</span>
          </button>

          {/* Document Upload Button */}
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow-sm shadow-blue-500/20 transition-all"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload Document</span>
          </button>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-slate-500 hover:text-slate-700 rounded-lg hover:bg-slate-100 relative transition-colors"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full ring-2 ring-white"></span>
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-dropdown p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">System Notifications</h4>
                  <span className="text-[10px] bg-blue-50 text-blue-700 font-semibold px-2 py-0.5 rounded-full">
                    2 New
                  </span>
                </div>

                <div className="py-2 space-y-3">
                  <div className="flex gap-3 text-xs">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-800">Q3 Financial Report Indexed</p>
                      <p className="text-slate-500 text-[11px]">142 vector chunks stored in FAISS.</p>
                      <span className="text-[10px] text-slate-400">5 mins ago</span>
                    </div>
                  </div>

                  <div className="flex gap-3 text-xs">
                    <FilePlus className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-800">New RAG Engine Update</p>
                      <p className="text-slate-500 text-[11px]">PyPDF parser speed optimized by 35%.</p>
                      <span className="text-[10px] text-slate-400">1 hour ago</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Upload Modal */}
      <UploadModal isOpen={showUploadModal} onClose={() => setShowUploadModal(false)} />
    </>
  );
}
