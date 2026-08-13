import React from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Bot,
  LineChart,
  FileSpreadsheet,
  User,
  Settings,
  LogOut,
  Sparkles,
  ChevronRight,
  ShieldCheck,
  HardDrive
} from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { useDocStore } from '../store/useDocStore';

export default function Sidebar({ mobileOpen, setMobileOpen }) {
  const { user, logout } = useAuthStore();
  const { documents } = useDocStore();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/app/dashboard', icon: LayoutDashboard },
    { name: 'Documents', path: '/app/documents', icon: FileText, badge: documents.length },
    { name: 'AI Workspace', path: '/app/workspace', icon: Bot, highlight: true },
    { name: 'Insights', path: '/app/insights', icon: LineChart },
    { name: 'Reports', path: '/app/reports', icon: FileSpreadsheet },
    { name: 'Profile', path: '/app/profile', icon: User },
  ];

  return (
    <>
      {/* Mobile overlay backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 left-0 z-50 h-screen w-64 bg-white border-r border-slate-200 flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Top Header & Brand */}
        <div>
          <div className="h-16 px-6 flex items-center justify-between border-b border-slate-100">
            <NavLink to="/app/dashboard" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <span className="font-extrabold text-slate-900 text-lg tracking-tight">NexaDocs</span>
                <span className="block text-[10px] uppercase font-bold text-blue-600 tracking-wider">Enterprise AI</span>
              </div>
            </NavLink>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Workspace Navigation
            </div>

            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <NavLink
                  key={item.name}
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold shadow-sm border border-blue-100'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 ${
                        isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>

                  {item.badge !== undefined && (
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      isActive ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {item.badge}
                    </span>
                  )}

                  {item.highlight && (
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Bottom Section: Storage & User Info */}
        <div className="p-4 border-t border-slate-100 space-y-4">
          {/* Storage Meter Widget */}
          <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/80">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1.5">
              <div className="flex items-center gap-1.5">
                <HardDrive className="w-3.5 h-3.5 text-blue-600" />
                <span>Storage Plan</span>
              </div>
              <span className="text-slate-500 font-normal">
                {user?.storageUsed || 1.42} GB / {user?.storageLimit || 10} GB
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full transition-all duration-300"
                style={{ width: `${((user?.storageUsed || 1.42) / (user?.storageLimit || 10)) * 100}%` }}
              />
            </div>
          </div>

          {/* User Account Card */}
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50/50 hover:bg-slate-100/80 transition-colors">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-9 h-9 rounded-full bg-slate-900 text-white font-semibold flex items-center justify-center text-xs shrink-0 ring-2 ring-blue-500/20">
                {user?.name ? user.name.split(' ').map(n => n[0]).join('').substring(0, 2) : 'SJ'}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-semibold text-slate-900 truncate">
                  {user?.name || 'Sarah Jenkins'}
                </div>
                <div className="text-[11px] text-slate-500 truncate flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-600 shrink-0" />
                  <span className="truncate">{user?.plan || 'Enterprise Pro'}</span>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>

          {/* Developer Attribution */}
          <div className="pt-2 text-center text-[10px] text-slate-400 border-t border-slate-100">
            Built by <a href="https://github.com/VenkataKarthikeya-eng" target="_blank" rel="noreferrer" className="font-semibold text-slate-600 hover:text-blue-600 transition-colors">CHERUKURI VENKATA KARTHIKEYA</a>
          </div>
        </div>
      </aside>
    </>
  );
}
