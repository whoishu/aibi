import { useState, useEffect, useRef } from 'react';

interface Suggestion {
  text: string;
  score: number;
  source: string;
  metadata?: {
    keywords?: string[];
    doc_id?: string;
  };
}

interface AutocompleteResponse {
  query: string;
  suggestions: Suggestion[];
  total: number;
}

interface AutocompleteProps {
  apiUrl?: string;
  userId?: string;
  limit?: number;
}

const Autocomplete: React.FC<AutocompleteProps> = ({
  apiUrl = '/api/v1/autocomplete',
  userId = 'demo-user',
  limit = 10,
}) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (query.trim().length === 0) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Debounce API calls
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      fetchSuggestions(query);
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query]);

  const fetchSuggestions = async (searchQuery: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          user_id: userId,
          limit: limit,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: AutocompleteResponse = await response.json();
      setSuggestions(data.suggestions);
      setShowSuggestions(true);
      setSelectedIndex(-1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch suggestions');
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (selectedSuggestion: string) => {
    try {
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          selected_suggestion: selectedSuggestion,
          user_id: userId,
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    setQuery(suggestion.text);
    setShowSuggestions(false);
    setSuggestions([]);
    submitFeedback(suggestion.text);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionClick(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        break;
    }
  };

  return (
    <div className="autocomplete-container">
      <div className="search-box">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          placeholder="输入查询内容 (例如: 销售, 客户, 市场)..."
          className="search-input"
        />
        {loading && <div className="loading-indicator">搜索中...</div>}
      </div>

      {error && <div className="error-message">{error}</div>}

      {showSuggestions && suggestions.length > 0 && (
        <div className="suggestions-list">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className={`suggestion-item ${
                index === selectedIndex ? 'selected' : ''
              }`}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="suggestion-text">{suggestion.text}</div>
              <div className="suggestion-meta">
                <span className="suggestion-source">{suggestion.source}</span>
                <span className="suggestion-score">
                  {suggestion.score.toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Autocomplete;
