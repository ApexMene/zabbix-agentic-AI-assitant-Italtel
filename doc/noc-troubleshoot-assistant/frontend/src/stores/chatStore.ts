import { create } from 'zustand';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface ChatState {
  investigationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  setInvestigationId: (id: string | null) => void;
  addMessage: (message: Message) => void;
  appendToLastMessage: (text: string) => void;
  setStreaming: (streaming: boolean) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  investigationId: null,
  messages: [],
  isStreaming: false,
  
  setInvestigationId: (id) => set({ investigationId: id }),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  appendToLastMessage: (text) => set((state) => {
    const messages = [...state.messages];
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      lastMessage.content += text;
    }
    return { messages };
  }),
  
  setStreaming: (streaming) => set({ isStreaming: streaming }),
  
  clearChat: () => set({ 
    investigationId: null, 
    messages: [], 
    isStreaming: false 
  }),
}));
