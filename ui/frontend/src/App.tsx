import React, { useState } from 'react';
import AttackForm from './components/AttackForm';
import ImagePreview from './components/ImagePreview';
import ResultsDisplay from './components/ResultsDisplay'; 
import { AttackResult } from './types';

const App: React.FC = () => {
  // States for file and preview
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('mobilenet_v2');

  
  // States for attack results
  const [results, setResults] = useState<AttackResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  return (
    <div
      style={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: '#222',
        color: '#fff',
        padding: '20px'
      }}
    >
      {/* Left Panel */}
      <div
        style={{
          width: '450px',
          backgroundColor: '#333',
          padding: '20px',
          borderRadius: '8px',
          marginRight: '20px'
        }}
      >
        <h1>Fast Gradient Sign Method</h1>
        <AttackForm 
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          setPreview={setPreview}
          setResults={setResults}
          setIsLoading={setIsLoading}
        />

        {/* Image Preview */}
        {preview && (
          <ImagePreview preview={preview} />
        )}
      </div>

      {/* Right Panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <h2>Attack Results</h2>
        
        {isLoading ? (
          <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <p>Processing attack...</p>
          </div>
        ) : (
          results && <ResultsDisplay results={results} />
        )}
      </div>
    </div>
  );
};

export default App;