import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage } from '../api/ApiClient';

export default function ChatInterface() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem('session_id') || 'session-' + Date.now());
  const [messages, setMessages] = useState([
    { sender: 'assistant', text: 'Kiemaen Core Agent initialized. Active multi-agent pipeline ready.', agent_metadata: { framework: 'LangGraph/FastAPI', mode: 'active' } }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('session_id', sessionId);
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Optimistic UI rendering
    const updatedMessages = [...messages, { sender: 'user', text: userMessage }];
    setMessages(updatedMessages);
    setLoading(true);

    try {
      const response = await sendChatMessage({ session_id: sessionId, message: userMessage });
      setMessages([...updatedMessages, { 
        sender: 'assistant', 
        text: response.reply, 
        agent_metadata: response.agent_metadata 
      }]);
    } catch (err) {
      setMessages([...updatedMessages, { 
        sender: 'assistant', 
        text: '[Network Error] Failed to reach live backend via tunnel.', 
        agent_metadata: { mode: 'error' } 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (promptText) => {
    setInput(promptText);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-900 text-gray-100 font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-gray-800 border-b border-gray-700 shadow-md">
        <div>
          <h1 className="text-lg font-bold tracking-wide text-indigo-400">Kiemaen Multi-Agent AI</h1>
          <p className="text-xs text-gray-400">Session: {sessionId}</p>
        </div>
        <button 
          onClick={() => {
            const newId = 'session-' + Date.now();
            setSessionId(newId);
            setMessages([{ sender: 'assistant', text: 'New session started. How can I assist you?', agent_metadata: { mode: 'active' } }]);
          }}
          className="px-3 py-1.5 text-xs font-medium bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors border border-gray-600"
        >
          New Session
        </button>
      </header>

      {/* Dynamic Context Chips / Quick Prompts */}
      <div className="flex gap-2 px-6 py-3 bg-gray-850 border-b border-gray-800 overflow-x-auto whitespace-nowrap">
        <button onClick={() => handleQuickPrompt("Analyze beam deflection and superposition theory")} className="px-3 py-1 text-xs bg-indigo-900/40 text-indigo-300 border border-indigo-700/50 rounded-full hover:bg-indigo-900/60">
          Structural Analysis
        </button>
        <button onClick={() => handleQuickPrompt("Update project risk matrix and critical path")} className="px-3 py-1 text-xs bg-emerald-900/40 text-emerald-300 border border-emerald-700/50 rounded-full hover:bg-emerald-900/60">
          Project Management
        </button>
        <button onClick={() => handleQuickPrompt("Verify LangGraph worker-reviewer execution loop")} className="px-3 py-1 text-xs bg-purple-900/40 text-purple-300 border border-purple-700/50 rounded-full hover:bg-purple-900/60">
          LangGraph Pipeline
        </button>
      </div>

      {/* Chat Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-xl rounded-2xl px-4 py-3 text-sm shadow-sm leading-relaxed ${
              msg.sender === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-none' 
                : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-bl-none'
            }`}>
              <p className="whitespace-pre-wrap">{msg.text}</p>
            </div>
            
            {msg.agent_metadata && (
              <div className="flex items-center gap-2 mt-1 px-1 text-[10px] text-gray-400">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>{msg.agent_metadata.framework || 'Agent'} ({msg.agent_metadata.mode})</span>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-gray-400 px-2 py-1">
            <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce"></div>
            <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce delay-100"></div>
            <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce delay-200"></div>
            <span>Agent processing execution loop...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-4 bg-gray-800 border-t border-gray-700 flex gap-3">
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask structural, project management, or coding agents..."
          className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-100 focus:outline-none focus:border-indigo-500 placeholder-gray-500"
        />
        <button 
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-3 rounded-xl font-medium text-sm transition-colors shadow-md"
        >
          Send
        </button>
      </form>
    </div>
  );
}
