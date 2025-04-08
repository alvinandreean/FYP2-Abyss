import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import { AttackResult } from '../types';
import ModelSelector from './ModelSelector';
import { useNavigate } from 'react-router-dom';

interface AttackFormProps {
  selectedFile: File | null;
  setSelectedFile: (file: File | null) => void;
  setPreview: (preview: string | null) => void;
  setResults: (results: AttackResult | null) => void;
  setIsLoading: (isLoading: boolean) => void;
}

const AttackForm: React.FC<AttackFormProps> = ({
  selectedFile,
  setSelectedFile,
  setPreview,
  setResults,
  setIsLoading
}) => {
  const [epsilon, setEpsilon] = useState<number>(0.05);
  const [autoTune, setAutoTune] = useState<boolean>(false);
  const [selectedModel, setSelectedModel] = useState<string>("mobilenet_v2");

  // Get a navigate function from React Router:
  const navigate = useNavigate();

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('autoTune', autoTune.toString());
    formData.append('model', selectedModel);

    // Only include epsilon if autoTune is NOT checked
    if (!autoTune) {
      formData.append('epsilon', epsilon.toString());
    }

    try {
      const res = await axios.post('http://localhost:5000/attack', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = res.data;

      const processedResults: AttackResult = {
        ...data,
        // Convert returned strings to data URLs:
        original_image: `data:image/png;base64,${data.original_image}`,
        perturbation_image: `data:image/png;base64,${data.perturbation_image}`,
        adversarial_image: `data:image/png;base64,${data.adversarial_image}`
      };

      // Set the results in local state if you still want it in AttackPage
      setResults(processedResults);

      // Navigate to /results and pass the processedResults in 'state'
      navigate('/results', { state: { results: processedResults } });
    } catch (error) {
      console.error("Error processing attack:", error);
      alert('Error processing attack');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* File Upload */}
      <div style={{ marginBottom: '40px' }}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
      </div>

      {/* Model Selector */}
      <ModelSelector 
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
      />

      {/* Epsilon Slider */}
      <div style={{ marginBottom: '40px' }}>
        <label style={{ marginRight: '5px' }}>
          Epsilon: {epsilon.toFixed(5)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.00001"
          value={epsilon}
          onChange={(e) => setEpsilon(Number(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>

      {/* Auto-Tune Checkbox */}
      <div style={{ marginBottom: '40px' }}>
        <label style={{ marginRight: '10px' }}>
          <input
            type="checkbox"
            checked={autoTune}
            onChange={(e) => setAutoTune(e.target.checked)}
            style={{ marginRight: '10px' }}
          />
          Auto-Tune Epsilon
        </label>
      </div>

      {/* Submit Button */}
      <button 
        type="submit" 
        style={{ 
          padding: '10px 16px', 
          cursor: 'pointer',
          backgroundColor: '#4a90e2',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontSize: '16px'
        }}
      >
        Run Attack
      </button>
    </form>
  );
};

export default AttackForm;
