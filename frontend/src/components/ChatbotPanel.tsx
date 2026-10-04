import React, { useState, useEffect, useRef } from 'react';
import { useChatbotStore } from '../store/chatbotStore';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  is_demo?: boolean;
}

export function ChatbotPanel() {
  const { isOpen, toggleOpen, setOpen, contextData } = useChatbotStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMsg, setInputMsg] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    if (isOpen && !sessionId && !loading) {
      setLoading(true);
      fetch('/api/v1/chatbot/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voyage_plan_id: null, navigation_session_id: null })
      })
      .then(r => r.json())
      .then(data => {
        setSessionId(data.session_id);
        return fetch(`/api/v1/chatbot/sessions/${data.session_id}/messages`);
      })
      .then(r => r.json())
      .then(data => {
        setMessages(data.messages);
      })
      .catch(e => console.error("Chatbot init error:", e))
      .finally(() => setLoading(false));
    }
  }, [isOpen, sessionId]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (msgOverride?: string) => {
    const msgText = msgOverride || inputMsg;
    if (!msgText.trim() || !sessionId || loading) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: msgText }];
    setMessages(newMessages);
    setInputMsg('');
    setLoading(true);

    try {
      const res = await fetch(`/api/v1/chatbot/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msgText,
          context: contextData
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, data]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. The assistant is currently unreachable.' }]);
    } finally {
      setLoading(false);
    }
  };

  const quickQuestions = [
    "Why was this route selected?",
    "What is the current risk?",
    "What are the alternative routes?",
    "Why is the rejected route not feasible?",
    "What is our current navigation status?",
    "What happens if the route is reassessed?"
  ];

  return (
    <>
      {/* Floating Button */}
      <button 
        onClick={toggleOpen}
        aria-label="Open Captain Voyage Assistant"
        className="fixed bottom-6 right-6 z-[9999] w-14 h-14 bg-[#1E40AF] hover:bg-[#1E3A8A] text-white rounded-full shadow-xl flex items-center justify-center transition-transform hover:scale-105"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>

      {/* Slide-in Drawer */}
      <div 
        className={`fixed top-0 right-0 h-full w-[400px] max-w-full bg-white shadow-2xl z-[10000] transform transition-transform duration-300 flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* Header */}
        <div className="bg-[#1E40AF] text-white p-4 flex items-center justify-between">
          <div>
            <h2 className="font-telemetry font-bold text-lg">Captain Voyage Assistant</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="w-2 h-2 rounded-full bg-green-400"></span>
              <span className="text-xs font-telemetry-sm opacity-90">Demo / Fallback</span>
            </div>
          </div>
          <button 
            onClick={() => setOpen(false)}
            className="text-white hover:bg-white/20 p-2 rounded-full transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 bg-slate-50 flex flex-col gap-4 font-telemetry-sm text-sm">
          {messages.map((m, i) => (
            <div key={i} className={`flex flex-col max-w-[85%] ${m.role === 'user' ? 'self-end' : 'self-start'}`}>
              <div className={`p-3 rounded-2xl ${m.role === 'user' ? 'bg-[#1E40AF] text-white rounded-tr-none' : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-sm'}`}>
                {m.content}
              </div>
              {m.role === 'assistant' && m.is_demo && (
                <span className="text-[10px] text-slate-400 mt-1 ml-1 font-telemetry-xs">Generated by Demo Assistant</span>
              )}
            </div>
          ))}
          {loading && (
            <div className="self-start bg-white border border-slate-200 p-3 rounded-2xl rounded-tl-none shadow-sm text-slate-500 flex items-center gap-2">
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length > 0 && !loading && (
          <div className="p-2 bg-white border-t border-slate-100 flex gap-2 overflow-x-auto whitespace-nowrap hide-scrollbar">
            {quickQuestions.map((q, i) => (
              <button 
                key={i} 
                onClick={() => handleSend(q)}
                className="text-xs font-telemetry-sm bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 flex-shrink-0 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="flex items-center gap-2"
          >
            <input 
              type="text" 
              value={inputMsg}
              onChange={e => setInputMsg(e.target.value)}
              placeholder="Ask the voyage assistant..."
              className="flex-1 border border-slate-300 rounded-full px-4 py-2 font-telemetry-sm text-sm focus:outline-none focus:border-[#1E40AF] focus:ring-1 focus:ring-[#1E40AF]"
            />
            <button 
              type="submit"
              disabled={!inputMsg.trim() || loading}
              className="w-10 h-10 rounded-full bg-[#1E40AF] text-white flex items-center justify-center disabled:opacity-50 hover:bg-[#1E3A8A] transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
