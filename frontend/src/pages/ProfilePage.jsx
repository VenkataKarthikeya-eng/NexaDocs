import React, { useState } from 'react';
import {
  User,
  Mail,
  Building,
  ShieldCheck,
  HardDrive,
  Key,
  LogOut,
  CheckCircle2,
  Lock,
  Sparkles,
  Save
} from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { toast } from '../store/useToastStore';

export default function ProfilePage() {
  const { user, updateProfile, logout } = useAuthStore();
  const [name, setName] = useState(user?.name || 'Sarah Jenkins');
  const [company, setCompany] = useState(user?.company || 'NexusTech Global');
  const [role, setRole] = useState(user?.role || 'Principal Product Manager');
  const [saved, setSaved] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    const res = await updateProfile({ name, company, role });
    if (res?.success) {
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      toast.success("Profile changes saved successfully!");
    } else {
      toast.error(res?.error || "Failed to update profile.");
    }
  };

  return (
    <div className="max-w-4xl space-y-8 animate-in fade-in duration-300">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Account & Profile Settings</h1>
        <p className="text-xs text-slate-500 mt-1">
          Manage your enterprise profile, security credentials, storage quota, and subscription plan.
        </p>
      </div>

      {/* Main Profile Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left Column: Editable Profile Details */}
        <div className="md:col-span-7 bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center gap-4 pb-6 border-b border-slate-100">
            <div className="w-16 h-16 rounded-full bg-slate-900 text-white font-extrabold text-xl flex items-center justify-center ring-4 ring-blue-500/20">
              {name.split(' ').map(n => n[0]).join('').substring(0, 2)}
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 text-lg">{name}</h3>
              <p className="text-xs text-slate-500">{user?.email}</p>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full mt-1 border border-blue-100">
                <ShieldCheck className="w-3 h-3 text-blue-600" />
                {user?.plan || 'Enterprise Pro'}
              </span>
            </div>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Company / Organization</label>
              <div className="relative">
                <Building className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Job Title</label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              <span>{saved ? 'Changes Saved!' : 'Save Profile Changes'}</span>
            </button>
          </form>
        </div>

        {/* Right Column: Storage & API Keys */}
        <div className="md:col-span-5 space-y-6">
          {/* Storage Quota */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-blue-600" />
                Storage Breakdown
              </h4>
              <span className="text-xs font-bold text-slate-600">
                {user?.storageUsed || 1.42} GB / {user?.storageLimit || 10} GB
              </span>
            </div>

            <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full"
                style={{ width: `${((user?.storageUsed || 1.42) / (user?.storageLimit || 10)) * 100}%` }}
              />
            </div>

            <p className="text-[11px] text-slate-500 leading-relaxed">
              Storage includes PDF original source files and FAISS vector embedding indices.
            </p>
          </div>

          {/* Developer API Token */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
            <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Key className="w-4 h-4 text-blue-600" />
              API Key & Secret
            </h4>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-700 truncate">
              nexadocs_live_sk_849204918239019283
            </div>

            <p className="text-[11px] text-slate-500">
              Use this bearer key to authenticate REST endpoints with FastAPI.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
