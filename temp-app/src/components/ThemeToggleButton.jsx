import React, { useState, useEffect } from 'react';

export function ThemeToggleButton() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    document.body.style.background = dark ? '#1a202c' : '#ffffff';
    document.body.style.color = dark ? '#cbd5e0' : '#1a202c';
  }, [dark]);

  return (
    <button
      onClick={() => setDark(!dark)}
      style={{
        background: dark ? '#4a5568' : '#e2e8f0',
        color: dark ? '#fff' : '#000',
        border: 'none',
        padding: '6px 12px',
        borderRadius: '6px',
        cursor: 'pointer'
      }}
    >
      {dark ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}
