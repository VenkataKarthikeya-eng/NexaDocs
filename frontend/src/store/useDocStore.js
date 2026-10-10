import { create } from 'zustand';
import api from '../services/api';

const SAMPLE_DOCUMENTS = [
  {
    id: 'doc-1',
    title: 'Enterprise Financial Report.pdf',
    filename: 'Enterprise_Financial_Report.pdf',
    fileSize: '4.8 MB',
    pageCount: 38,
    chunkCount: 142,
    status: 'Ready',
    category: 'Finance',
    createdAt: '2026-08-10',
    summary: 'Comprehensive financial report detailing Q3 enterprise revenue growth ($42.5M, +24% YoY), EBITDA margins (31.2%), and capital allocation toward cloud data infrastructure.',
    topics: ['Revenue Growth', 'EBITDA Margin', 'CapEx Allocation', 'Supply Chain Risk', 'Market Expansion'],
    entities: [
      { name: 'Total Q3 Revenue', type: 'Metric', detail: '$42.5 Million (+24%)' },
      { name: 'AI Infrastructure Budget', type: 'Financial', detail: '$8.2 Million' },
      { name: 'Deloitte Auditing Group', type: 'Organization', detail: 'External Auditor' },
      { name: 'Target Q4 Growth', type: 'Forecast', detail: '28% YoY expansion' }
    ],
    highlights: [
      { page: 4, text: 'Operating expenses decreased by 6.4% due to automated document intelligence pipelines.' },
      { page: 12, text: 'Cloud infrastructure unit economics improved with 99.99% service availability.' }
    ]
  },
  {
    id: 'doc-2',
    title: 'AI Research Paper.pdf',
    filename: 'AI_Research_Paper.pdf',
    fileSize: '6.1 MB',
    pageCount: 52,
    chunkCount: 210,
    status: 'Ready',
    category: 'Research',
    createdAt: '2026-08-04',
    summary: 'Peer-reviewed research study examining the deployment of retrieval-augmented generation models, vector similarity indexing, and citation matching in clinical diagnostics and software compliance.',
    topics: ['Clinical RAG', 'FDA Compliance', 'Medical Diagnostics', 'FAISS Indexing', 'NLP Extraction'],
    entities: [
      { name: 'Diagnostic Precision', type: 'Metric', detail: '94.8% accuracy score' },
      { name: 'FDA Software Standard', type: 'Regulatory', detail: 'Class II Software Medical Device' },
      { name: 'Stanford Medical Labs', type: 'Partner', detail: 'Research Institution' }
    ],
    highlights: [
      { page: 14, text: 'Document intelligence platforms reduced diagnostic transcription time by 42%.' }
    ]
  },
  {
    id: 'doc-3',
    title: 'Technical Architecture Document.pdf',
    filename: 'Technical_Architecture_Document.pdf',
    fileSize: '2.3 MB',
    pageCount: 22,
    chunkCount: 88,
    status: 'Ready',
    category: 'Engineering',
    createdAt: '2026-08-12',
    summary: 'Technical architecture specification outlining FAISS vector indexing, smart recursive chunking algorithms, PyPDF text extraction, FastAPI async backend, and React Zustand frontend integration.',
    topics: ['FAISS Indexing', 'FastAPI Backend', 'RAG Retrieval', 'Vector Embeddings', 'JWT Auth'],
    entities: [
      { name: 'SentenceTransformers', type: 'AI Framework', detail: 'all-MiniLM-L6-v2 model' },
      { name: 'FAISS Vector DB', type: 'Database', detail: 'FlatL2 Indexing for 100k+ docs' },
      { name: 'FastAPI / Uvicorn', type: 'Backend', detail: 'Async ASGI Python framework' },
      { name: 'PyPDF / PDFPlumber', type: 'Extractor', detail: 'Multi-threaded text & table parser' }
    ],
    highlights: [
      { page: 2, text: 'RAG retrieval latency targeted at under 180ms for enterprise document querying.' },
      { page: 8, text: 'FAISS index automatically regenerated upon incremental document uploads.' }
    ]
  }
];

export const useDocStore = create((set, get) => ({
  documents: [],
  activeDoc: null,
  isLoadingDocs: false,
  searchQuery: '',
  categoryFilter: 'All',
  isUploading: false,
  uploadProgress: 0,
  error: null,

  setSearchQuery: (query) => set({ searchQuery: query }),
  setCategoryFilter: (category) => set({ categoryFilter: category }),
  setActiveDoc: (doc) => set({ activeDoc: doc }),

  fetchDocuments: async () => {
    set({ isLoadingDocs: true });
    try {
      const response = await api.get('/documents');
      if (response && response.data) {
        const docs = response.data;
        set((state) => ({
          documents: docs,
          activeDoc: docs.length > 0 ? (docs.find(d => d.id === state.activeDoc?.id) || docs[0]) : null,
          isLoadingDocs: false,
          error: null
        }));
      }
    } catch (e) {
      console.warn("Backend fetch error:", e);
      set({ isLoadingDocs: false });
    }
  },

  uploadDocument: async (file) => {
    set({ isUploading: true, uploadProgress: 20, error: null });

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            set({ uploadProgress: Math.min(pct, 90) });
          }
        }
      });

      if (response && response.data) {
        const newDoc = response.data;
        set((state) => ({
          documents: [newDoc, ...state.documents.filter(d => d.id !== newDoc.id)],
          activeDoc: newDoc,
          isUploading: false,
          uploadProgress: 100,
          error: null
        }));

        setTimeout(() => set({ uploadProgress: 0 }), 1000);
        return { success: true, doc: newDoc };
      }
      throw new Error("Upload failed: No data returned from server");
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed';
      set({ isUploading: false, uploadProgress: 0, error: msg });
      return { success: false, error: msg };
    }
  },

  deleteDocument: async (docId) => {
    try {
      await api.delete(`/documents/${docId}`);
      set((state) => {
        const updatedDocs = state.documents.filter((d) => d.id !== docId);
        const nextActive = state.activeDoc?.id === docId ? (updatedDocs[0] || null) : state.activeDoc;
        return {
          documents: updatedDocs,
          activeDoc: nextActive
        };
      });
      return { success: true };
    } catch (err) {
      console.error('Document delete error:', err);
      return { success: false, error: err.response?.data?.detail || err.message };
    }
  },

  getFilteredDocuments: () => {
    const { documents, searchQuery, categoryFilter } = get();
    return documents.filter((doc) => {
      const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            (doc.summary && doc.summary.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesCategory = categoryFilter === 'All' || doc.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }
}));
