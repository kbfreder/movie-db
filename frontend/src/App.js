import React, { useState } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Search, Database, Code, Info } from 'lucide-react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [schema, setSchema] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post('/api/query', { query: query.trim() });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while processing your query');
    } finally {
      setLoading(false);
    }
  };

  const loadSchema = async () => {
    try {
      const response = await axios.get('/api/schema');
      setSchema(response.data);
    } catch (err) {
      console.error('Failed to load schema:', err);
    }
  };

  const exampleQueries = [
    "Find all movies with Russell Crowe",
    "Show me action movies from 2020",
    "Who directed Gladiator?",
    "List movies with Tom Hanks",
    "Find movies with both Russell Crowe and Tom Hanks",
    "Show me the top 10 movies by year",
    "Find all directors of action movies"
  ];

  return (
    <div className="container">
      <header className="header">
        <h1>🎬 Movie Database Query</h1>
        <p>Ask questions about movies, actors, and directors in natural language</p>
      </header>

      <div className="card">
        <form onSubmit={handleSubmit} className="query-form">
          <div className="input-group">
            <Search className="search-icon" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about movies, actors, or directors..."
              className="input"
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn" disabled={loading || !query.trim()}>
            {loading ? <span className="loading"></span> : 'Search'}
          </button>
        </form>

        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results && (
          <div className="results">
            <div className="result-section">
              <h3><Code size={20} /> Generated Cypher Query</h3>
              <SyntaxHighlighter 
                language="cypher" 
                style={tomorrow}
                customStyle={{ borderRadius: '8px', fontSize: '14px' }}
              >
                {results.cypher_query}
              </SyntaxHighlighter>
            </div>

            <div className="result-section">
              <h3><Database size={20} /> Results</h3>
              <div className="results-content">
                {results.results && results.results.length > 0 ? (
                  <pre className="results-json">
                    {JSON.stringify(results.results, null, 2)}
                  </pre>
                ) : (
                  <p>No results found</p>
                )}
              </div>
            </div>

            {results.explanation && (
              <div className="result-section">
                <h3><Info size={20} /> Explanation</h3>
                <p>{results.explanation}</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card">
        <h3>💡 Example Queries</h3>
        <div className="examples">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="example-btn"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>📊 Database Schema</h3>
        <button onClick={loadSchema} className="btn">
          Load Schema Info
        </button>
        {schema && (
          <div className="schema-info">
            <h4>Nodes:</h4>
            <ul>
              {Object.entries(schema.nodes).map(([nodeType, info]) => (
                <li key={nodeType}>
                  <strong>{nodeType}</strong> ({info.count} nodes)
                  <br />
                  <small>Properties: {info.properties.join(', ')}</small>
                </li>
              ))}
            </ul>
            <h4>Relationships:</h4>
            <ul>
              {Object.entries(schema.relationships).map(([relType, description]) => (
                <li key={relType}>
                  <strong>{relType}</strong>: {description}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 