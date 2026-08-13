import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Sparkles, Mail, Lock, User, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';

export default function AuthPages() {
  const location = useLocation();
  const navigate = useNavigate();
  const isRegisterPage = location.pathname.includes('register');

  const [name, setName] = useState('');
  const [email, setEmail] = useState('sarah.j@enterprise.com');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState('');

  const { login, register, isLoading } = useAuthStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!email || !password || (isRegisterPage && !name)) {
      setFormError('Please complete all required fields.');
      return;
    }

    let result;
    if (isRegisterPage) {
      result = await register(name, email, password);
    } else {
      result = await login(email, password);
    }

    if (result.success) {
      navigate('/app/dashboard');
    } else {
      setFormError(result.error || 'Authentication failed');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-5xl bg-white border border-slate-200 rounded-3xl shadow-dropdown overflow-hidden grid grid-cols-1 md:grid-cols-12 min-h-[640px]">

        {/* Left Side: Form */}
        <div className="md:col-span-6 p-8 sm:p-12 flex flex-col justify-between">
          <div>
            {/* Header / Logo */}
            <Link to="/" className="flex items-center gap-2.5 mb-8">
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
                <Sparkles className="w-5 h-5" />
              </div>
              <span className="font-extrabold text-slate-900 text-lg tracking-tight">NexaDocs</span>
            </Link>

            <div className="mb-6">
              <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {isRegisterPage ? 'Create your NexaDocs account' : 'Welcome back to NexaDocs'}
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                {isRegisterPage
                  ? 'Access your intelligent document workspace in seconds.'
                  : 'Sign in to access your indexed documents and AI insights.'}
              </p>
            </div>

            {/* Error Banner */}
            {formError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-700 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            {/* Auth Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {isRegisterPage && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                  <div className="relative">
                    <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Sarah Jenkins"
                      className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Work Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-9 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 shadow-md shadow-blue-500/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2 mt-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Signing in...</span>
                  </>
                ) : (
                  <>
                    <span>{isRegisterPage ? 'Create Account' : 'Sign In'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Toggle Register / Login */}
          <div className="pt-6 border-t border-slate-100 text-center text-xs text-slate-500">
            {isRegisterPage ? (
              <p>
                Already have an account?{' '}
                <Link to="/login" className="font-bold text-blue-600 hover:underline">
                  Sign in here
                </Link>
              </p>
            ) : (
              <p>
                Don't have an account yet?{' '}
                <Link to="/register" className="font-bold text-blue-600 hover:underline">
                  Create an account
                </Link>
              </p>
            )}
          </div>
        </div>

        {/* Right Side: Enterprise Visual Banner */}
        <div className="hidden md:flex md:col-span-6 bg-slate-900 text-white p-12 flex-col justify-between relative overflow-hidden">
          <div className="relative z-10 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>SOC2 Type II Compliant Architecture</span>
            </div>

            <h3 className="text-3xl font-extrabold tracking-tight leading-snug">
              Instant PDF Chunking & Vector Search Engine
            </h3>

            <ul className="space-y-4 text-xs text-slate-300">
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <span>PyPDF & PDFPlumber deep textual extraction layer.</span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <span>FAISS vector indexing for high-speed k-NN similarity search.</span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <span>Page-level citation references for 100% auditability.</span>
              </li>
            </ul>
          </div>

          <div className="relative z-10 p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs text-slate-300 space-y-1">
            <p className="font-bold text-white">Need a quick demo?</p>
            <p className="text-[11px] text-slate-400">
              You can click <strong>Sign In</strong> directly to enter the demo workspace preloaded with enterprise financial & engineering documents.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
