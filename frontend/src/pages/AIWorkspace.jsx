import React, { useState, useRef, useEffect } from 'react';
import {
  FileText,
  Bot,
  Send,
  Sparkles,
  Layers,
  Search,
  BookOpen,
  Tag,
  Building,
  CheckSquare,
  RefreshCw,
  Square,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useDocStore } from '../store/useDocStore';
import { useChatStore } from '../store/useChatStore';
import { toast } from '../store/useToastStore';

export default function AIWorkspace() {
  const { documents, activeDoc, setActiveDoc, fetchDocuments } = useDocStore();
  const { getMessagesForDoc, askQuestionStream, loadChatHistory, isThinking, clearChat } = useChatStore();

  const [inputQuery, setInputQuery] = useState('');
  const [docSearch, setDocSearch] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const currentDoc = activeDoc || documents[0];
  const messages = currentDoc ? getMessagesForDoc(currentDoc.id) : [];

  useEffect(() => {
    if (currentDoc?.id) {
      loadChatHistory(currentDoc.id);
    }
  }, [currentDoc?.id]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || !currentDoc || isThinking || isStreaming) return;

    const queryText = inputQuery;
    setInputQuery('');
    
    abortControllerRef.current = new AbortController();
    setIsStreaming(true);

    const result = await askQuestionStream(currentDoc.id, queryText, abortControllerRef.current.signal);
    setIsStreaming(false);
    abortControllerRef.current = null;

    if (result?.success) {
      toast.success("AI response completed with page citations.");
    } else if (result?.aborted) {
      toast.info("AI token generation stopped.");
    }
  };

  const handleStopStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsStreaming(false);
  };

  const handlePromptChipClick = async (promptText) => {
    if (isThinking || isStreaming || !currentDoc) return;
    abortControllerRef.current = new AbortController();
    setIsStreaming(true);
    await askQuestionStream(currentDoc.id, promptText, abortControllerRef.current.signal);
    setIsStreaming(false);
    abortControllerRef.current = null;
  };

  const filteredDocList = documents.filter((d) =>
    d.title.toLowerCase().includes(docSearch.toLowerCase()) ||
    d.filename.toLowerCase().includes(docSearch.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-6.5rem)] flex flex-col bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Workspace Header Bar */}
      <div className="h-14 bg-slate-50 border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <span>AI Document Intelligence Workspace</span>
              <span className="text-[10px] bg-blue-100 text-blue-800 font-extrabold px-2 py-0.5 rounded-full uppercase tracking-wider">
                SSE Stream & FAISS
              </span>
            </h2>
            <p className="text-[11px] text-slate-500">
              Active: <strong className="text-slate-800">{currentDoc?.filename || 'No document selected'}</strong>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => {
              if (currentDoc) {
                clearChat(currentDoc.id);
                toast.info("Conversation cleared.");
              }
            }}
            className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg text-slate-600 font-semibold transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
            <span>Clear Chat</span>
          </button>
        </div>
      </div>

      {/* 3-Panel Main Workspace Body */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 divide-y lg:divide-y-0 lg:divide-x divide-slate-200 overflow-hidden">

        {/* LEFT PANEL: Document Navigation */}
        <div className="lg:col-span-3 bg-slate-50/60 p-4 flex flex-col justify-between overflow-y-auto space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                Select Document
              </h3>
              <span className="text-[10px] text-slate-500 font-semibold">{documents.length} Files</span>
            </div>

            {/* Quick Search Document */}
            <div className="relative mb-3">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={docSearch}
                onChange={(e) => setDocSearch(e.target.value)}
                placeholder="Filter documents..."
                className="w-full pl-8 pr-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Document Selector List */}
            {filteredDocList.length > 0 ? (
              <div className="space-y-2 max-h-56 lg:max-h-80 overflow-y-auto pr-1">
                {filteredDocList.map((doc) => {
                  const isSelected = currentDoc?.id === doc.id;
                  return (
                    <button
                      key={doc.id}
                      onClick={() => setActiveDoc(doc)}
                      className={`w-full text-left p-3 rounded-xl border text-xs transition-all flex items-start gap-2.5 ${
                        isSelected
                          ? 'bg-white border-blue-600 shadow-sm text-slate-900 ring-1 ring-blue-500/20'
                          : 'bg-white/60 border-slate-200/90 text-slate-600 hover:bg-white hover:border-slate-300'
                      }`}
                    >
                      <FileText className={`w-4 h-4 shrink-0 mt-0.5 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                      <div className="min-w-0 flex-1">
                        <p className={`font-bold truncate ${isSelected ? 'text-blue-900' : 'text-slate-800'}`}>
                          {doc.title}
                        </p>
                        <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-1">
                          <span>{doc.pageCount} pgs</span>
                          <span>•</span>
                          <span>{doc.chunkCount} vector chunks</span>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 px-2 text-xs text-slate-400 bg-white/50 rounded-xl border border-dashed border-slate-200">
                <p className="font-semibold text-slate-600 mb-1">No Documents Available</p>
                <p className="text-[11px] text-slate-400">Upload a PDF to start asking AI questions.</p>
              </div>
            )}
          </div>

          {/* Vector Index Metadata Box */}
          {currentDoc && (
            <div className="bg-white border border-slate-200 rounded-xl p-3.5 space-y-2 text-xs">
              <h4 className="font-bold text-slate-900 text-xs flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-blue-600" />
                Knowledge Index Status
              </h4>
              <div className="space-y-1 text-[11px] text-slate-600">
                <div className="flex justify-between">
                  <span>File Size:</span>
                  <strong className="text-slate-900">{currentDoc.fileSize}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Pages Parsed:</span>
                  <strong className="text-slate-900">{currentDoc.pageCount} Pages</strong>
                </div>
                <div className="flex justify-between">
                  <span>Vector Chunks:</span>
                  <strong className="text-slate-900">{currentDoc.chunkCount} (FAISS)</strong>
                </div>
                <div className="flex justify-between">
                  <span>Status:</span>
                  <strong className="text-emerald-600 font-bold uppercase">{currentDoc.status || 'READY'}</strong>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* CENTER PANEL: AI Conversation Chat & Streaming */}
        <div className="lg:col-span-5 bg-white flex flex-col justify-between overflow-hidden">
          {/* Conversation Log */}
          <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
            {messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1`}
                >
                  <div className="flex items-center gap-2 text-[10px] text-slate-400 font-medium">
                    <span>{isUser ? 'You' : 'NexaDocs AI Intelligence'}</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                  </div>

                  <div
                    className={`p-4 rounded-2xl text-xs max-w-xl leading-relaxed ${
                      isUser
                        ? 'bg-blue-600 text-white rounded-tr-xs shadow-xs font-medium'
                        : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-xs space-y-3'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.text}</p>

                    {/* Source Citation Cards */}
                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div className="pt-2.5 border-t border-slate-200/80 space-y-1.5">
                        <div className="text-[10px] font-extrabold uppercase text-slate-400 flex items-center gap-1">
                          <BookOpen className="w-3 h-3 text-blue-600" />
                          Source Citations:
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.citations.map((c, i) => (
                            <div
                              key={i}
                              className="bg-white border border-slate-200 p-2 rounded-lg text-[11px] text-slate-800 shadow-2xs hover:border-blue-300 transition-colors flex items-center gap-2"
                            >
                              <span className="font-extrabold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">
                                📄 Page {c.page}
                              </span>
                              <span className="font-medium truncate max-w-[140px]">{c.section}</span>
                              {c.relevance_score && (
                                <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                                  {Math.round(c.relevance_score * 100)}% Match
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Thinking & Stream State */}
            {(isThinking || isStreaming) && (
              <div className="flex items-center justify-between text-xs text-slate-600 bg-slate-50 border border-slate-200 p-3.5 rounded-2xl max-w-md animate-pulse">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600 shrink-0" />
                  <span>Streaming tokens from FAISS RAG pipeline...</span>
                </div>
                {isStreaming && (
                  <button
                    onClick={handleStopStream}
                    className="flex items-center gap-1 px-2.5 py-1 bg-white border border-slate-200 rounded text-[11px] font-bold text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <Square className="w-3 h-3 fill-red-600" />
                    <span>Stop</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Suggested Prompt Chips */}
          <div className="px-4 py-2 bg-slate-50/50 border-t border-slate-100 flex items-center gap-2 overflow-x-auto text-[11px]">
            <span className="font-bold text-slate-400 shrink-0 uppercase tracking-wider text-[10px]">Prompts:</span>
            {[
              "Executive summary",
              "Key financial metrics",
              "Security & SOC2 SLA",
              "Technical architecture"
            ].map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handlePromptChipClick(`Give me a breakdown of ${chip} in ${currentDoc?.filename}`)}
                className="px-2.5 py-1 bg-white border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 rounded-lg text-slate-700 font-medium whitespace-nowrap transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Chat Input Bar */}
          <form onSubmit={handleSend} className="p-4 border-t border-slate-200 bg-white">
            <div className="relative">
              <input
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                placeholder={currentDoc ? `Ask any question about ${currentDoc.filename}...` : "Select a document first..."}
                disabled={!currentDoc || isThinking || isStreaming}
                className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
              />
              <button
                type="submit"
                disabled={!inputQuery.trim() || !currentDoc || isThinking || isStreaming}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-all shadow-xs"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        </div>

        {/* RIGHT PANEL: AI Document Insights */}
        <div className="lg:col-span-4 bg-slate-50/50 p-4 sm:p-6 overflow-y-auto space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <h3 className="font-extrabold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-blue-600" />
              Automated Document Insights
            </h3>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
              Extracted
            </span>
          </div>

          {currentDoc ? (
            <div className="space-y-5 text-xs">
              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-2">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider text-blue-600">
                  Executive Summary
                </h4>
                <p className="text-slate-600 leading-relaxed text-xs">
                  {currentDoc.summary}
                </p>
              </div>

              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-blue-600" />
                  Key Topics Identified
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {currentDoc.topics?.map((topic, i) => (
                    <span
                      key={i}
                      className="bg-blue-50 text-blue-800 border border-blue-100 px-2.5 py-1 rounded-lg text-xs font-semibold"
                    >
                      #{topic}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Building className="w-3.5 h-3.5 text-blue-600" />
                  Extracted Entities & Metrics
                </h4>

                <div className="space-y-2">
                  {currentDoc.entities?.map((ent, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-slate-900 block">{ent.name}</span>
                        <span className="text-[10px] text-slate-400 font-medium">{ent.type}</span>
                      </div>
                      <span className="text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded">
                        {ent.detail}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <CheckSquare className="w-3.5 h-3.5 text-emerald-600" />
                  Document Key Highlights
                </h4>

                <div className="space-y-2">
                  {currentDoc.highlights?.map((h, i) => (
                    <div key={i} className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex items-start gap-2">
                      <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded shrink-0 mt-0.5">
                        Pg {h.page}
                      </span>
                      <p className="leading-snug">{h.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400 text-xs">
              Select a document to inspect automated summaries and entities.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
