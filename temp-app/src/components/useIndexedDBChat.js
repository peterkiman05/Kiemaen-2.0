import { useState, useEffect } from 'react';

export function useIndexedDBChat(initialMessages = []) {
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem('kiemaen_chat_history');
      return saved ? JSON.parse(saved) : initialMessages;
    } catch (e) {
      return initialMessages;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('kiemaen_chat_history', JSON.stringify(messages));
    } catch (e) {
      console.error('Failed to save chat history', e);
    }
  }, [messages]);

  return [messages, setMessages];
}
