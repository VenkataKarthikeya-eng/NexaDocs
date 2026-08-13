import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  FileText,
  Search,
  Database,
  Cpu,
  Bot,
  CheckCircle2,
  Lock,
  Layers,
  ChevronRight,
  BarChart3,
  Globe2,
  Users,
  Mail
} from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen bg-white text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-slate-900 text-xl tracking-tight">NexaDocs</span>
              <span className="block text-[10px] uppercase font-bold text-blue-600 tracking-wider">Enterprise AI</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600">
            <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-blue-600 transition-colors">How It Works</a>
            <a href="#pricing" className="hover:text-blue-600 transition-colors">Pricing</a>
            <a href="#security" className="hover:text-blue-600 transition-colors">Security SLA</a>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 text-slate-700 font-semibold text-sm hover:text-blue-600 transition-colors"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all flex items-center gap-2"
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-24 overflow-hidden bg-gradient-to-b from-slate-50/50 via-white to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Introducing NexaDocs RAG v2.4 Engine</span>
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
              <span className="text-blue-600 font-bold hover:underline cursor-pointer">Read Technical Specs →</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
              Transform Unstructured Documents into <span className="text-blue-600">Actionable AI Intelligence</span>
            </h1>

            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed font-normal max-w-2xl mx-auto">
              Upload complex PDFs, financial audits, SLAs, and research papers. Process instantly with multi-layered RAG vector search, exact page citations, and enterprise summaries.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <button
                onClick={() => navigate('/register')}
                className="w-full sm:w-auto px-8 py-4 bg-blue-600 text-white rounded-xl font-bold text-base hover:bg-blue-700 shadow-lg shadow-blue-500/25 transition-all flex items-center justify-center gap-2 group"
              >
                <span>Start Free 14-Day Trial</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => navigate('/app/workspace')}
                className="w-full sm:w-auto px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-xl font-bold text-base hover:bg-slate-50 hover:border-slate-300 shadow-xs transition-all flex items-center justify-center gap-2"
              >
                <Bot className="w-5 h-5 text-blue-600" />
                <span>Launch Live Product Sandbox</span>
              </button>
            </div>

            {/* Enterprise Trust Indicators */}
            <div className="pt-8 flex flex-wrap items-center justify-center gap-8 text-slate-400 text-xs font-semibold">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span className="text-slate-600">SOC2 Type II Certified</span>
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-blue-600" />
                <span className="text-slate-600">AES-256 Encrypted</span>
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-600" />
                <span className="text-slate-600">FAISS Vector Engine</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-500" />
                <span className="text-slate-600">&lt;180ms Latency</span>
              </div>
            </div>
          </div>

          {/* Interactive Live Demo Preview Box */}
          <div className="mt-16 max-w-5xl mx-auto bg-white border border-slate-200 rounded-2xl shadow-dropdown overflow-hidden">
            {/* Window Top Controls */}
            <div className="bg-slate-100/80 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                <span className="ml-2 text-xs font-semibold text-slate-500">
                  NexaDocs 3-Panel AI Workspace Demo
                </span>
              </div>

              <div className="flex bg-white rounded-lg p-0.5 border border-slate-200 text-xs font-semibold">
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`px-3 py-1 rounded-md transition-colors ${
                    activeTab === 'chat' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  RAG Chat
                </button>
                <button
                  onClick={() => setActiveTab('insights')}
                  className={`px-3 py-1 rounded-md transition-colors ${
                    activeTab === 'insights' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Extracted Insights
                </button>
              </div>
            </div>

            {/* Interactive Sandbox Body */}
            <div className="grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-slate-200 bg-white">
              {/* Document Tree Panel */}
              <div className="md:col-span-3 p-4 bg-slate-50/50 space-y-3">
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">Active Document</div>
                <div className="bg-white p-3 rounded-xl border border-blue-200 shadow-xs flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                    PDF
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-900 truncate">Q3_Financial_Audit.pdf</p>
                    <p className="text-[10px] text-slate-500">38 pgs • 142 Chunks</p>
                  </div>
                </div>

                <div className="space-y-1.5 pt-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase">Vector Indices</div>
                  <div className="text-xs text-slate-700 bg-white p-2 rounded-lg border border-slate-200 flex items-center justify-between">
                    <span>Revenue Breakdown</span>
                    <span className="text-[10px] text-emerald-600 font-bold">Page 4</span>
                  </div>
                  <div className="text-xs text-slate-700 bg-white p-2 rounded-lg border border-slate-200 flex items-center justify-between">
                    <span>AI CapEx Allocation</span>
                    <span className="text-[10px] text-emerald-600 font-bold">Page 12</span>
                  </div>
                </div>
              </div>

              {/* Center Panel (Chat / Insights) */}
              <div className="md:col-span-9 p-6 space-y-4">
                {activeTab === 'chat' ? (
                  <div className="space-y-4">
                    {/* User Question */}
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-xs text-xs max-w-md font-medium shadow-xs">
                        What were our top revenue drivers and EBITDA margins in Q3?
                      </div>
                    </div>

                    {/* AI Response */}
                    <div className="flex gap-3 items-start">
                      <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-xs shrink-0">
                        <Sparkles className="w-4 h-4 text-blue-400" />
                      </div>
                      <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-tl-xs p-4 text-xs text-slate-800 space-y-2 max-w-xl">
                        <p>
                          According to <strong>Page 4 (Section 2.1)</strong> of <em>Q3_Financial_Audit.pdf</em>, total revenue reached <strong>$42.5 Million (+24% YoY)</strong>. EBITDA margin expanded to <strong>31.2%</strong>.
                        </p>
                        <div className="flex flex-wrap gap-2 pt-1 border-t border-slate-200/60 text-[11px]">
                          <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-semibold cursor-pointer">
                            [Citation: Page 4, Section 2.1]
                          </span>
                          <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-semibold">
                            [Chunk #42 - FAISS Similarity 0.94]
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 text-xs">
                    <div className="bg-blue-50/60 border border-blue-100 rounded-xl p-4">
                      <h4 className="font-bold text-blue-900 text-sm mb-1">Executive Summary</h4>
                      <p className="text-blue-800 leading-relaxed">
                        Comprehensive analysis of Q3 operations demonstrating strong margin expansion (+31.2% EBITDA) driven by enterprise AI automation. Strategic investments in cloud data infrastructure projected to yield 28% YoY growth in Q4.
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="border border-slate-200 rounded-xl p-3 bg-slate-50">
                        <span className="font-bold text-slate-900 block mb-2">Key Entities Extracted</span>
                        <ul className="space-y-1.5 text-slate-600">
                          <li className="flex justify-between"><span>Revenue:</span> <strong className="text-slate-900">$42.5M</strong></li>
                          <li className="flex justify-between"><span>EBITDA Margin:</span> <strong className="text-slate-900">31.2%</strong></li>
                          <li className="flex justify-between"><span>Auditor:</span> <strong className="text-slate-900">Deloitte</strong></li>
                        </ul>
                      </div>

                      <div className="border border-slate-200 rounded-xl p-3 bg-slate-50">
                        <span className="font-bold text-slate-900 block mb-2">Topic Clusters</span>
                        <div className="flex flex-wrap gap-1.5">
                          <span className="bg-white border border-slate-200 px-2 py-1 rounded text-slate-700 font-semibold">#CapEx Optimization</span>
                          <span className="bg-white border border-slate-200 px-2 py-1 rounded text-slate-700 font-semibold">#EBITDA Expansion</span>
                          <span className="bg-white border border-slate-200 px-2 py-1 rounded text-slate-700 font-semibold">#SupplyChain</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid Section */}
      <section id="features" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
            <h2 className="text-xs font-extrabold uppercase tracking-wider text-blue-600">Enterprise Capability</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Engineered for Enterprise Knowledge Teams
            </p>
            <p className="text-slate-600 text-base">
              Built on battle-tested document extractors, FAISS vector indexing, and zero-leakage enterprise AI protocols.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 hover:border-blue-300 hover:shadow-card-hover transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center mb-6 shadow-md shadow-blue-500/20">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Smart PDF Parsing</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                PyPDF and PDFPlumber extract complex multi-column layouts, tables, header metadata, and raw text layers automatically.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 hover:border-blue-300 hover:shadow-card-hover transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center mb-6 shadow-md shadow-blue-500/20">
                <Database className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">FAISS Vector Indexing</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Recursive text chunking with sentence transformer embeddings stores document vectors in FAISS for sub-180ms retrieval.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 hover:border-blue-300 hover:shadow-card-hover transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center mb-6 shadow-md shadow-blue-500/20">
                <Bot className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Exact Page Citations</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Every AI answer includes clickable citation badges that jump directly to the original page and chunk in the source PDF.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 hover:border-blue-300 hover:shadow-card-hover transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center mb-6 shadow-md shadow-blue-500/20">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Automated Insights</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Instant generation of executive summaries, key topics, monetary metrics, organizations, and compliance checklists.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 hover:border-blue-300 hover:shadow-card-hover transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center mb-6 shadow-md shadow-blue-500/20">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">SOC2 Privacy SLA</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Complete tenant isolation. Your documents remain encrypted with AES-256 and are never fed into public LLM training datasets.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 hover:border-blue-300 hover:shadow-card-hover transition-all">
              <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center mb-6 shadow-md shadow-blue-500/20">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">RESTful API & FastAPI</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Seamless API endpoints (`/upload`, `/chat`, `/analyze`, `/documents`) allowing easy integration into existing enterprise workflows.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-slate-50/50 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
            <h2 className="text-xs font-extrabold uppercase tracking-wider text-blue-600">Workflow</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              4 Steps from Document to Intelligence
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3 relative">
              <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 font-extrabold flex items-center justify-center mx-auto text-sm">
                1
              </div>
              <h4 className="font-bold text-slate-900 text-base">Upload Document</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Drag and drop PDF files into the secure NexaDocs document library.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3 relative">
              <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 font-extrabold flex items-center justify-center mx-auto text-sm">
                2
              </div>
              <h4 className="font-bold text-slate-900 text-base">Smart Vector Index</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                PyPDF extracts text and FAISS generates dense 384-dim semantic embeddings.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3 relative">
              <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 font-extrabold flex items-center justify-center mx-auto text-sm">
                3
              </div>
              <h4 className="font-bold text-slate-900 text-base">RAG Q&A Chat</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Ask questions in natural language and receive context-backed answers.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center space-y-3 relative">
              <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 font-extrabold flex items-center justify-center mx-auto text-sm">
                4
              </div>
              <h4 className="font-bold text-slate-900 text-base">Export & Report</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Export executive summaries, extracted entities, and compliance audit reports.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
            <h2 className="text-xs font-extrabold uppercase tracking-wider text-blue-600">Pricing</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Transparent Enterprise Pricing
            </p>
            <p className="text-slate-600 text-base">
              Scale document intelligence across your team with predictable monthly tiers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:border-slate-300 transition-all flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Starter</h3>
                <p className="text-xs text-slate-500 mt-1">For individual analysts & researchers</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-slate-900">$29</span>
                  <span className="text-slate-500 text-xs font-semibold"> / month</span>
                </div>
                <ul className="space-y-3 text-xs text-slate-600 mb-8">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Up to 50 PDF Uploads/mo</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> 5GB Vector Storage</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Standard FAISS Indexing</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Page-level Citations</li>
                </ul>
              </div>
              <button
                onClick={() => navigate('/register')}
                className="w-full py-3 bg-slate-50 text-slate-700 font-bold border border-slate-200 rounded-xl hover:bg-slate-100 text-xs transition-colors"
              >
                Get Started
              </button>
            </div>

            <div className="bg-white border-2 border-blue-600 rounded-2xl p-8 shadow-xl shadow-blue-500/10 relative flex flex-col justify-between">
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">
                Most Popular
              </span>
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Enterprise Pro</h3>
                <p className="text-xs text-slate-500 mt-1">For high-growth document intelligence teams</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-slate-900">$99</span>
                  <span className="text-slate-500 text-xs font-semibold"> / month</span>
                </div>
                <ul className="space-y-3 text-xs text-slate-600 mb-8">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Unlimited PDF Documents</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> 50GB High-Speed Vector DB</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Automated Executive Summaries</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Structured Entity Extraction</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Priority FastAPI Queue</li>
                </ul>
              </div>
              <button
                onClick={() => navigate('/register')}
                className="w-full py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 text-xs shadow-md shadow-blue-500/20 transition-all"
              >
                Start 14-Day Trial
              </button>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:border-slate-300 transition-all flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Custom Enterprise</h3>
                <p className="text-xs text-slate-500 mt-1">Dedicated cloud instance & custom SLAs</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-slate-900">Custom</span>
                </div>
                <ul className="space-y-3 text-xs text-slate-600 mb-8">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Dedicated On-Premises FAISS Cluster</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> SOC2 Type II SLA & HIPAA Audit</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> Custom LLM / Local Model fine-tuning</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /> 24/7 Dedicated Solutions Engineer</li>
                </ul>
              </div>
              <button
                onClick={() => navigate('/register')}
                className="w-full py-3 bg-slate-50 text-slate-700 font-bold border border-slate-200 rounded-xl hover:bg-slate-100 text-xs transition-colors"
              >
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer Banner */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Ready to Unlock Document Intelligence?
          </h2>
          <p className="text-blue-100 text-base max-w-xl mx-auto">
            Join thousands of analysts, engineering teams, and legal professionals processing documents effortlessly with NexaDocs.
          </p>
          <button
            onClick={() => navigate('/register')}
            className="px-8 py-4 bg-white text-blue-600 font-extrabold rounded-xl text-base hover:bg-blue-50 shadow-lg transition-all"
          >
            Create Your Account Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6 text-xs">
          <div className="flex items-center gap-3 text-white font-bold">
            <Sparkles className="w-4 h-4 text-blue-500" />
            <span>NexaDocs © 2026 Enterprise Inc.</span>
          </div>

          {/* Professional Developer Attribution */}
          <div className="flex flex-col sm:flex-row items-center gap-3 bg-slate-800/80 px-4 py-2 rounded-xl border border-slate-700/60 text-slate-300">
            <span className="font-medium text-[11px]">
              Built by <strong className="text-white font-bold">CHERUKURI VENKATA KARTHIKEYA</strong>
            </span>
            <div className="flex items-center gap-3 text-slate-400">
              <a
                href="mailto:venkatakarthikeya2005@gmail.com"
                className="hover:text-blue-400 transition-colors flex items-center gap-1"
                title="Email Developer"
              >
                <Mail className="w-3.5 h-3.5" />
                <span className="hidden sm:inline text-[11px]">Email</span>
              </a>
              <a
                href="https://github.com/VenkataKarthikeya-eng"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white transition-colors flex items-center gap-1"
                title="GitHub Profile"
              >
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                <span className="hidden sm:inline text-[11px]">GitHub</span>
              </a>
              <a
                href="https://www.linkedin.com/in/cherukuri-venkata-karthikeya-4b54393ab/"
                target="_blank"
                rel="noreferrer"
                className="hover:text-blue-400 transition-colors flex items-center gap-1"
                title="LinkedIn Profile"
              >
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                <span className="hidden sm:inline text-[11px]">LinkedIn</span>
              </a>
            </div>
          </div>

          <div className="flex gap-6">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="#security" className="hover:text-white transition-colors">Security SLA</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
