import { create } from 'zustand';
import api from '../services/api';
import { useDocStore } from './useDocStore';

export const useChatStore = create((set, get) => ({
  chats: {},
  isThinking: false,
  activePrompt: '',

  getMessagesForDoc: (docId) => {
    const docMessages = get().chats[docId];
    if (docMessages && docMessages.length > 0) {
      return docMessages;
    }
    const doc = useDocStore.getState().documents.find(d => d.id === docId) || useDocStore.getState().activeDoc;
    return [
      {
        id: 'msg-init-' + docId,
        sender: 'assistant',
        text: `Document **${doc?.filename || doc?.title || 'Selected document'}** is indexed into FAISS vector database. Ask any question to retrieve answers with exact page citations!`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations: []
      }
    ];
  },

  loadChatHistory: async (docId) => {
    if (!docId) return;
    try {
      const res = await api.get(`/ai/chat/history/${docId}`);
      if (res && res.data && res.data.length > 0) {
        const formatted = [];
        res.data.forEach((item) => {
          formatted.push({
            id: 'user-' + item.id,
            sender: 'user',
            text: item.question,
            timestamp: item.timestamp
          });
          formatted.push({
            id: 'bot-' + item.id,
            sender: 'assistant',
            text: item.answer,
            timestamp: item.timestamp,
            citations: item.sources || []
          });
        });
        set((state) => ({
          chats: {
            ...state.chats,
            [docId]: formatted
          }
        }));
      }
    } catch (e) {
      // History endpoint optional
    }
  },

  askQuestionStream: async (docId, questionText, abortSignal) => {
    if (!questionText.trim()) return;

    const userMsg = {
      id: 'msg-user-' + Date.now(),
      sender: 'user',
      text: questionText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const botMsgId = 'msg-bot-' + Date.now();
    const botMsg = {
      id: botMsgId,
      sender: 'assistant',
      text: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      citations: []
    };

    // Add user message & empty placeholder bot message
    set((state) => {
      const currentDocMessages = state.chats[docId] || [];
      return {
        chats: {
          ...state.chats,
          [docId]: [...currentDocMessages, userMsg, botMsg]
        },
        isThinking: true
      };
    });

    const token = localStorage.getItem('nexadocs_token');
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

    try {
      const response = await fetch(`${apiBase}/ai/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify({
          document_id: docId,
          question: questionText
        }),
        signal: abortSignal
      });

      if (!response.ok) {
        throw new Error(`Streaming failed: HTTP ${response.status}`);
      }

      set({ isThinking: false });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let accumulatedText = '';
      let citations = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            try {
              const data = JSON.parse(trimmed.replace(/^data:\s*/, ''));
              if (data.type === 'start') {
                citations = data.sources || [];
                set((state) => {
                  const msgs = (state.chats[docId] || []).map((m) =>
                    m.id === botMsgId ? { ...m, citations } : m
                  );
                  return { chats: { ...state.chats, [docId]: msgs } };
                });
              } else if (data.type === 'token') {
                accumulatedText += data.text || '';
                set((state) => {
                  const msgs = (state.chats[docId] || []).map((m) =>
                    m.id === botMsgId ? { ...m, text: accumulatedText } : m
                  );
                  return { chats: { ...state.chats, [docId]: msgs } };
                });
              }
            } catch (err) {
              console.warn("SSE chunk parse warning:", err);
            }
          }
        }
      }
      return { success: true };
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log("Stream generation stopped by user.");
        return { success: false, aborted: true };
      }

      // Fallback to static POST /ai/chat if stream interrupted
      try {
        const fallbackRes = await api.post('/ai/chat', {
          document_id: docId,
          question: questionText
        });
        if (fallbackRes && fallbackRes.data) {
          set((state) => {
            const msgs = (state.chats[docId] || []).map((m) =>
              m.id === botMsgId
                ? {
                    ...m,
                    text: fallbackRes.data.answer,
                    citations: fallbackRes.data.sources || []
                  }
                : m
            );
            return { chats: { ...state.chats, [docId]: msgs }, isThinking: false };
          });
          return { success: true };
        }
      } catch (fallbackErr) {
        set((state) => {
          const msgs = (state.chats[docId] || []).map((m) =>
            m.id === botMsgId
              ? {
                  ...m,
                  text: `Error generating response: ${err.message || "Failed to communicate with AI engine."}`,
                  citations: []
                }
              : m
          );
          return { chats: { ...state.chats, [docId]: msgs }, isThinking: false };
        });
        return { success: false, error: err.message };
      }
    } finally {
      set({ isThinking: false });
    }
  },

  askQuestion: async (docId, questionText) => {
    return get().askQuestionStream(docId, questionText, null);
  },

  clearChat: (docId) => {
    set((state) => ({
      chats: {
        ...state.chats,
        [docId]: []
      }
    }));
  }
}));
