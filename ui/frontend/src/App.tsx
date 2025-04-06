import React, { useState, ChangeEvent, useEffect } from 'react';
import axios from 'axios';

const App: React.FC = () => {
  // States for file, preview, and results
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [attackInfo, setAttackInfo] = useState<any>(null);

  // States for epsilon slider and auto-tune toggle
  const [epsilon, setEpsilon] = useState<number>(0.05);
  const [autoTune, setAutoTune] = useState<boolean>(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFile(file);

      // Generate a preview URL for the selected file
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
      const response = await axios.post('http://localhost:5000/attack', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAttackInfo(response.data);
      setResultImage(`data:image/png;base64,${response.data.result_image}`);
    } catch (error) {
      console.error(error);
    }
  };

  // Clean up the preview URL when component unmounts or preview changes
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
        flexDirection: 'column',
        alignItems: 'center',       // center horizontally
        justifyContent: 'center',   // center vertically
        minHeight: '100vh',
        backgroundColor: '#222',
        color: '#fff',
        padding: '20px'
      }}
    >
      <h1 style={{ marginBottom: '20px' }}>FGSM Attack</h1>

      {/* Content Container */}
      <div
        style={{
          width: '400px',           // fixed width (adjust as desired)
          backgroundColor: '#333',
          padding: '20px',
          borderRadius: '8px',
          textAlign: 'center'
        }}
      >
        {/* Form */}
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

        {/* Preview of Uploaded Image */}
        {preview && (
          <div style={{ margin: '20px 0' }}>
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

        {/* Attack Results */}
        {attackInfo && (
          <div style={{ margin: '20px 0' }}>
            <h3>Attack Results</h3>
            <p>Epsilon Used: {attackInfo.epsilon}</p>
            <p>Original Class: {attackInfo.original_class}</p>
            <p>Adversarial Class: {attackInfo.adversarial_class}</p>
          </div>
        )}

        {resultImage && (
          <div style={{ margin: '20px 0' }}>
            <img
              src={resultImage}
              alt="Attack Result"
              style={{
                maxWidth: '100%',
                border: '2px solid #555',
                borderRadius: '4px'
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
