import React from \"react\";

export const QuickSuggestionChips = ({ suggestions = [\"Add Dockerfile\", \"Show Terraform\", \"Write unit tests\"], onSelect }) => {
  return (
    <div className=\"suggestion-chips-container\" role=\"region\" aria-label=\"Quick suggestions\">
      {suggestions.map((suggestion, index) => (
        <button 
          key={index} 
          onClick={() => onSelect(suggestion)} 
          className=\"suggestion-chip\"
          aria-label={`Quick suggestion: ${suggestion}`}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
};
