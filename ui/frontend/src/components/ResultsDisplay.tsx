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
    <>
      {/* Row of 3 Images */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-evenly',
          alignItems: 'flex-start',
          marginBottom: '20px'
        }}
      >
        {/* Original Image */}
        <div style={{ textAlign: 'center' }}>
          <h3>Original Image</h3>
          <img
            src={original_image}
            alt="Original"
            style={{
              maxWidth: '300px',
              border: '2px solid #555',
              borderRadius: '4px'
            }}
          />
        </div>

        {/* Perturbation */}
        <div style={{ textAlign: 'center' }}>
          <h3>Perturbation</h3>
          <img
            src={perturbation_image}
            alt="Perturbation"
            style={{
              maxWidth: '300px',
              border: '2px solid #555',
              borderRadius: '4px'
            }}
          />
        </div>

        {/* Adversarial Image */}
        <div style={{ textAlign: 'center' }}>
          <h3>Adversarial Image</h3>
          <img
            src={adversarial_image}
            alt="Adversarial"
            style={{
              maxWidth: '300px',
              border: '2px solid #555',
              borderRadius: '4px'
            }}
          />
        </div>
      </div>

      {/* Classification Info */}
      <div style={{ textAlign: 'center', fontSize: '18px' }}>
        {model_used && (
          <p>
            <strong>Model Used:</strong> {model_used}
          </p>
        )}
        <p>
          <strong>Epsilon Used:</strong> {epsilon_used}
        </p>
        <p>
          <strong>Original Class:</strong> {orig_class} 
          {orig_conf !== null && ` (Conf: ${(orig_conf * 100).toFixed(2)}%)`}
        </p>
        <p>
          <strong>Adversarial Class:</strong> {adv_class}
          {adv_conf !== null && ` (Conf: ${(adv_conf * 100).toFixed(2)}%)`}
        </p>
      </div>
    </>
  );
};

export default ResultsDisplay;