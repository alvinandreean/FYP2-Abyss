import React, { useState, ChangeEvent, useEffect } from 'react';
import axios from 'axios';

const App: React.FC = () => {
  // States for file, preview, and results
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [perturbationImage, setPerturbationImage] = useState<string | null>(null);
  const [adversarialImage, setAdversarialImage] = useState<string | null>(null);

  const [epsilonUsed, setEpsilonUsed] = useState<number | null>(null);
  const [origClass, setOrigClass] = useState<string | null>(null);
  const [origConf, setOrigConf] = useState<number | null>(null);
  const [advClass, setAdvClass] = useState<string | null>(null);
  const [advConf, setAdvConf] = useState<number | null>(null);

  const [epsilon, setEpsilon] = useState<number>(0.05);
  const [autoTune, setAutoTune] = useState<boolean>(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFile(file);
      const objectUrl = URL.createObjectURL(file);
      setPreview(objectUrl);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('epsilon', epsilon.toString());
    formData.append('autoTune', autoTune.toString());

    try {
      const res = await axios.post('http://localhost:5000/attack', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const data = res.data;
      // Update states with returned info
      setEpsilonUsed(data.epsilon_used);
      setOrigClass(data.orig_class);
      setOrigConf(data.orig_conf);
      setAdvClass(data.adv_class);
      setAdvConf(data.adv_conf);

      setOriginalImage(`data:image/png;base64,${data.original_image}`);
      setPerturbationImage(`data:image/png;base64,${data.perturbation_image}`);
      setAdversarialImage(`data:image/png;base64,${data.adversarial_image}`);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

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
          width: '450px',          // Make this bigger than before
          backgroundColor: '#333',
          padding: '20px',
          borderRadius: '8px',
          marginRight: '20px'
        }}
      >
        <h1>FGSM Attack</h1>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <input type="file" accept="image/*" onChange={handleFileChange} />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ marginRight: '10px' }}>
              Epsilon: {epsilon.toFixed(3)}
            </label>
            <input
              type="range"
              min="0"
              max="0.1"
              step="0.001"
              value={epsilon}
              onChange={(e) => setEpsilon(Number(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ marginRight: '10px' }}>
              <input
                type="checkbox"
                checked={autoTune}
                onChange={(e) => setAutoTune(e.target.checked)}
              />
              Auto-Tune Epsilon
            </label>
          </div>
          <button type="submit" style={{ padding: '8px 16px', cursor: 'pointer' }}>
            Run Attack
          </button>
        </form>

        {/* Image Preview */}
        {preview && (
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <h3>Image Preview</h3>
            <img
              src={preview}
              alt="Preview"
              style={{
                maxWidth: '100%',
                border: '2px solid #555',
                borderRadius: '4px'
              }}
            />
          </div>
        )}
      </div>

      {/* Right Panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <h2>Attack Results</h2>

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
          {originalImage && (
            <div style={{ textAlign: 'center' }}>
              <h3>Original Image</h3>
              <img
                src={originalImage}
                alt="Original"
                style={{
                  maxWidth: '300px',   // Larger size
                  border: '2px solid #555',
                  borderRadius: '4px'
                }}
              />
            </div>
          )}

          {/* Perturbation */}
          {perturbationImage && (
            <div style={{ textAlign: 'center' }}>
              <h3>Perturbation</h3>
              <img
                src={perturbationImage}
                alt="Perturbation"
                style={{
                  maxWidth: '300px',
                  border: '2px solid #555',
                  borderRadius: '4px'
                }}
              />
            </div>
          )}

          {/* Adversarial Image */}
          {adversarialImage && (
            <div style={{ textAlign: 'center' }}>
              <h3>Adversarial Image</h3>
              <img
                src={adversarialImage}
                alt="Adversarial"
                style={{
                  maxWidth: '300px',
                  border: '2px solid #555',
                  borderRadius: '4px'
                }}
              />
            </div>
          )}
        </div>

        {/* Classification Info */}
        {(origClass || advClass) && (
          <div style={{ textAlign: 'center', fontSize: '18px' }}>
            <p>
              <strong>Epsilon Used:</strong> {epsilonUsed}
            </p>
            <p>
              <strong>Original Class:</strong> {origClass} 
              {origConf !== null && ` (Conf: ${(origConf * 100).toFixed(2)}%)`}
            </p>
            <p>
              <strong>Adversarial Class:</strong> {advClass}
              {advConf !== null && ` (Conf: ${(advConf * 100).toFixed(2)}%)`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
