import { useEffect, useState } from \"react\";
import localforage from \"localforage\";

export const useIndexedDBChat = (initialState = []) => {
  const [messages, setMessages] = useState(initialState);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    localforage.getItem(\"kiemaen_chat_history\").then((savedMessages) => {
      if (savedMessages) {
        setMessages(savedMessages);
      }
      setIsLoaded(true);
    }).catch(err => console.error(\"Failed to load chat history from IndexedDB\", err));
  }, []);

  useEffect(() => {
    if (isLoaded) {
      localforage.setItem(\"kiemaen_chat_history\", messages).catch(err => {
        console.error(\"Failed to save chat history to IndexedDB\", err);
      });
    }
  }, [messages, isLoaded]);

  return [messages, setMessages];
};
