import { useState } from 'react';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleDetect() {
    if (!inputText.trim()) {
      setError("Please enter some text.");
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/detect-pii', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'your-secret-key'
        },
        body: JSON.stringify({ text: inputText })
      });

      if (!response.ok) {
        throw new Error("Detection failed.");
      }

      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      console.error(err);
      setError('Error detecting PII.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>PII Detection Service</h1>
      
      <textarea
        rows="10"
        style={{ width: '100%', padding: '1rem', fontSize: '1rem' }}
        placeholder="Paste your text here..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
      />
      
      <button 
        onClick={handleDetect}
        style={{ marginTop: '1rem', padding: '0.5rem 1rem', fontSize: '1rem', cursor: 'pointer' }}
      >
        {loading ? 'Detecting...' : 'Detect PII'}
      </button>

      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}

      {results && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Detection Results</h2>
          {results.length === 0 && <p>No PII detected.</p>}
          {results.map(item => (
            <div key={item.index} style={{ marginBottom: '1.5rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
              <p><strong>Content:</strong> {item.content}</p>
              <p><strong>Contextual PII:</strong> {item.contextual_pii ? 'Yes' : 'No'}</p>
              <p><strong>Detected Fields:</strong> {item.other_fields.length > 0 ? item.other_fields.join(', ') : 'None'}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}