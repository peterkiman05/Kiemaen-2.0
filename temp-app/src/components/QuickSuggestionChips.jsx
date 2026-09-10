import React from 'react';

export function QuickSuggestionChips({ onSelect }) {
  const suggestions = [
    'Analyze project risks',
    'Generate agent loop code',
    'Review beam deflection',
    'Optimize Termux server'
  ];

  return (
    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
      {suggestions.map((item, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(item)}
          style={{
            background: '#e2e8f0',
            border: 'none',
            borderRadius: '16px',
            padding: '6px 12px',
            fontSize: '0.85rem',
            cursor: 'pointer'
          }}
        >
          {item}
        </button>
      ))}
    </div>
  );
}
