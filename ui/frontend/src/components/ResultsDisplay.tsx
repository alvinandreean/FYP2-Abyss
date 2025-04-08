import React from 'react';
import { AttackResult } from '../types';

interface ResultsDisplayProps {
  results: AttackResult;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const {
    epsilon_used,
    orig_class,
    orig_conf,
    adv_class,
    adv_conf,
    original_image,
    perturbation_image,
    adversarial_image,
    model_used
  } = results;

  return (
    <div
      style={{
        backgroundColor: '#333',
        borderRadius: '8px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        maxWidth: '1200px', // optional, to prevent super wide images
        margin: '0 auto',   // center horizontally
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '1.5rem' }}>Attack Results</h2>
        {model_used && (
          <p style={{ margin: '5px 0' }}>
            <strong>Model Used:</strong> {model_used}
          </p>
        )}
        <p style={{ margin: '5px 0' }}>
          <strong>Epsilon Used:</strong> {epsilon_used}
        </p>
      </div>

      {/* Flex row for the three images: Input + Noise = Adversarial */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '1rem',
          flexWrap: 'wrap', // so on smaller screens, images stack
          marginBottom: '20px'
        }}
      >
        {/* Original Image */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>
            Input
            <br />
            <small style={{ fontWeight: 'normal' }}>
              {orig_class} {orig_conf !== null && `(${(orig_conf * 100).toFixed(2)}%)`}
            </small>
          </h3>
          <img
            src={original_image}
            alt="Original"
            style={{
              width: '100%',
              maxWidth: '250px',
              border: '2px solid #555',
              borderRadius: '4px'
            }}
          />
        </div>

        {/* Plus sign */}
        <div>
          <h2 style={{ margin: 0 }}>+</h2>
        </div>

        {/* Perturbation */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Perturbation</h3>
          <img
            src={perturbation_image}
            alt="Perturbation"
            style={{
              width: '100%',
              maxWidth: '250px',
              border: '2px solid #555',
              borderRadius: '4px'
            }}
          />
        </div>

        {/* Equals sign */}
        <div>
          <h2 style={{ margin: 0 }}>=</h2>
        </div>

        {/* Adversarial Image */}
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>
            Adversarial
            <br />
            <small style={{ fontWeight: 'normal' }}>
              {adv_class} {adv_conf !== null && `(${(adv_conf * 100).toFixed(2)}%)`}
            </small>
          </h3>
          <img
            src={adversarial_image}
            alt="Adversarial"
            style={{
              width: '100%',
              maxWidth: '250px',
              border: '2px solid #555',
              borderRadius: '4px'
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
