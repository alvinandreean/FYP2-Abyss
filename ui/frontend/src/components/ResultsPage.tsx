import React from 'react';
import { useLocation } from 'react-router-dom';
import ResultsDisplay from '../components/ResultsDisplay';
import Navbar from './Navbar';
import { AttackResult } from '../types';

const ResultsPage: React.FC = () => {
  const location = useLocation();
  const { results } = location.state as { results: AttackResult };

  if (!results) {
    return (
      <div
        style={{
          width: '100%',
          minHeight: '100vh',
          backgroundColor: '#222',
          color: '#fff',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Navbar />
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <h2 style={{ marginBottom: '1rem' }}>Attack Results</h2>
          <p>No results found. Please run an attack first.</p>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        backgroundColor: '#222',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Navbar />
      <div
        style={{
          padding: '20px',
          boxSizing: 'border-box'
        }}
      >
        {/* Renders the images and info in a nicely styled box */}
        <ResultsDisplay results={results} />
      </div>
    </div>
  );
};

export default ResultsPage;
