import React, { useState } from 'react';
import AttackForm from './AttackForm';
import ImagePreview from './ImagePreview';
import Navbar from './Navbar';
import { AttackResult } from '../types';

const AttackPage: React.FC = () => {
  // States for file, preview, isLoading, and results
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const setResults = useState<AttackResult | null>(null)[1];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        minHeight: '100vh',
        backgroundColor: '#222',
        color: '#fff',
        boxSizing: 'border-box'
      }}
    >
      <Navbar />
      
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          flex: 1,
          padding: '20px',
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
          {preview && <ImagePreview preview={preview} />}
        </div>

        {/* Right Panel */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <h2>Attack Page</h2>
          {isLoading ? (
            <div style={{ textAlign: 'center', marginTop: '50px' }}>
              <p>Processing attack...</p>
            </div>
          ) : (
            <p style={{ textAlign: 'center' }}>
              After running the attack, you&#39;ll be navigated to the results page.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AttackPage;
