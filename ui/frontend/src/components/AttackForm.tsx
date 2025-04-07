import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import { AttackResult } from '../types';
import ModelSelector from './ModelSelector';

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
  // Local state for epsilon, autoTune and the selected model
  const [epsilon, setEpsilon] = useState<number>(0.05);
  const [autoTune, setAutoTune] = useState<boolean>(false);
  // Use model values that match backend expected values (lowercase with underscores or similar)
  const [selectedModel, setSelectedModel] = useState<string>("mobilenet_v2");

  // Handle file input change: update selected file and preview URL
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFile(file);
      const objectUrl = URL.createObjectURL(file);
      setPreview(objectUrl);
    }
  };

  // Handle form submission: send all form data to the backend
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('autoTune', autoTune.toString());
    formData.append('model', selectedModel); // Pass selected model to backend
    
    // Only include epsilon in the request if autoTune is disabled
    if (!autoTune) {
      formData.append('epsilon', epsilon.toString());
    }

    try {
      const res = await axios.post('http://localhost:5000/attack', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const data = res.data;
      
      // Process returned images to add the data URL prefix
      const processedResults = {
        ...data,
        original_image: `data:image/png;base64,${data.original_image}`,
        perturbation_image: `data:image/png;base64,${data.perturbation_image}`,
        adversarial_image: `data:image/png;base64,${data.adversarial_image}`
      };
      
      setResults(processedResults);
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
