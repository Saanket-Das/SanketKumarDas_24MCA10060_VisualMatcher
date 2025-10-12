import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// A helper component for the loading spinner
const Spinner = () => <div className="spinner"></div>;

function App() {
  // State for inputs
  const [imageUrl, setImageUrl] = useState('');
  const [imageFile, setImageFile] = useState(null);
  
  // State for results and UI
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [minScore, setMinScore] = useState(0);

  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImageFile(file);
      // Clear the URL input if a file is chosen
      setImageUrl('');
    }
  };
  
  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!imageUrl && !imageFile) {
      setError('Please provide an image URL or upload a file.');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setResults([]);

    const formData = new FormData();
    if (imageFile) {
      formData.append('image_file', imageFile);
    } else {
      formData.append('image_url', imageUrl);
    }
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/search', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(response.data);
    } catch (err) {
      console.error(err);
      // Check for a network error specifically
      if (err.message === "Network Error") {
        setError('Network Error: Could not connect to the backend. Is it running?');
      } else {
        setError('An error occurred during the search.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Filter results based on the slider
  const filteredResults = results.filter(product => product.similarity >= minScore);

  return (
    <div className="container">
      <header className="header">
        <h1>Visual Product Matcher</h1>
        <p>Find visually similar products from an image.</p>
      </header>
      
      <main className="main-grid">
        {/* --- UPLOAD COLUMN --- */}
        <div className="card">
          <h2 className="card-title">Upload an Image</h2>
          <form onSubmit={handleSubmit} className="upload-form">
            {/* URL Input */}
            <div>
              <label htmlFor="url-input">Paste image URL</label>
              <input
                id="url-input"
                type="text"
                className="url-input"
                placeholder="https://example.com/image.jpg"
                value={imageUrl}
                onChange={(e) => {
                  setImageUrl(e.target.value);
                  // Clear file input if a URL is typed
                  if (imageFile) setImageFile(null);
                }}
              />
            </div>
            
            <div className="divider">OR</div>
            
            {/* File Input */}
            <div>
              <label htmlFor="file-input" className="file-input-button">
                Choose a File
              </label>
              <input
                id="file-input"
                type="file"
                onChange={handleFileChange}
                accept="image/*"
                style={{ display: 'none' }} 
              />
              {imageFile && <p className="file-name">{imageFile.name}</p>}
            </div>
            
            {/* Submit Button */}
            <button type="submit" className="submit-button" disabled={isLoading}>
              {isLoading && <Spinner />}
              {isLoading ? 'Searching...' : 'Search'}
            </button>
            
            {/* Error Message Display */}
            {error && <p className="error-message">{error}</p>}
          </form>
        </div>
        
        {/* --- RESULTS COLUMN --- */}
        <div className="card">
          <div className="results-header">
            <h2 className="card-title">Results</h2>
            {results.length > 0 && (
              <div className="filter-container">
                <label htmlFor="min-score">Min score: {Number(minScore).toFixed(0)}%</label>
                <input
                  id="min-score"
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={minScore}
                  onChange={(e) => setMinScore(e.target.value)}
                />
              </div>
            )}
          </div>
          
          {isLoading && <p>Loading...</p>}
          
          {!isLoading && results.length === 0 && (
            <div className="placeholder-container">
              <p>Your search results will appear here.</p>
            </div>
          )}
          
          <div className="results-grid">
            {filteredResults.map((product) => (
              <div key={product.id} className="product-card">
                <img src={product.imageUrl} alt={product.name} className="product-image" />
                <div className="product-info">
                  <p className="product-name">{product.name}</p>
                  <p className="product-similarity">
                    Similarity: {product.similarity.toFixed(2)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;