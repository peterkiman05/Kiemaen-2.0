import React, { useState } from 'react';
import { QuickSuggestionChips } from './components/QuickSuggestionChips';
import { ThemeToggleButton } from './components/ThemeToggleButton';
import { useIndexedDBChat } from './components/useIndexedDBChat';
import { useDebounce } from './hooks/useDebounce';
import { sendChatMessage } from './api/ApiClient';

export default function App() {
  const [messages, setMessages] = useIndexedDBChat([
    { sender: 'system', text: 'Welcome to Kiemaen AI Multi-Agent Platform.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const debouncedInput = useDebounce(input, 300);

  const handleSend = async (textToSend) => {
    const messageText = textToSend || input;
    if (!messageText.trim()) return;

    const newMessages = [...messages, { sender: 'user', text: messageText }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage({ session_id: 'default-session', message: messageText });
      setMessages([...newMessages, { sender: 'agent', text: response.reply, meta: response }]);
    } catch (err) {
      setMessages([...newMessages, { sender: 'system', text: 'Error connecting to backend agent.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Kiemaen AI</h1>
        <ThemeToggleButton />
      </header>

      <div style={{ border: '1px solid #ccc', borderRadius: '8px', height: '400px', overflowY: 'auto', padding: '15px', marginBottom: '15px', background: 'var(--bg-color, #f9f9f9)' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ margin: '10px 0', textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <span style={{ display: 'inline-block', padding: '10px 14px', borderRadius: '12px', background: msg.sender === 'user' ? '#007bff' : '#e2e8f0', color: msg.sender === 'user' ? '#fff' : '#000' }}>
              {msg.text}
            </span>
          </div>
        ))}
        {loading && <div style={{ fontStyle: 'italic', color: '#666' }}>Agent is thinking...</div>}
      </div>

      <QuickSuggestionChips onSelect={(suggestion) => handleSend(suggestion)} />

      <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your command or prompt..."
          style={{ flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }}
        />
        <button onClick={() => handleSend()} style={{ padding: '10px 20px', borderRadius: '6px', background: '#007bff', color: '#fff', border: 'none' }}>
          Send
        </button>
      </div>
      <div style={{ fontSize: '0.8rem', color: '#888', marginTop: '8px' }}>
        Debounced input value: {debouncedInput}
      </div>
    </div>
  );
}
