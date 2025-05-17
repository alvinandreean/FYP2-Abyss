import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import { AttackResult } from '../types';
import ModelSelector from './ModelSelector';
import ImageSelector from './ImageSelector';
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
  const [selectedImageUrl, setSelectedImageUrl] = useState<string | null>(null);

  // Get a navigate function from React Router:
  const navigate = useNavigate();

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setSelectedImageUrl(null); // Clear any selected URL image
    }
  };

  const handleImageSelect = (imageUrl: string) => {
    setSelectedImageUrl(imageUrl);
    setPreview(imageUrl);
    setSelectedFile(null); // Clear any selected file
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile && !selectedImageUrl) {
      alert('Please select an image file or choose an image from the available options');
      return;
    }

    setIsLoading(true);
    
    try {
      // Get the authentication token from localStorage
      const token = localStorage.getItem('token');
      let data;
      
      if (selectedFile) {
        // Handle file upload attack
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('autoTune', autoTune.toString());
        formData.append('model', selectedModel);
        
        // Only include epsilon if autoTune is NOT checked
        if (!autoTune) {
          formData.append('epsilon', epsilon.toString());
        }
        
        // Set up request headers with authentication token
        const headers: any = {
          'Content-Type': 'multipart/form-data'
        };
        
        if (token) {
          // Add the Authorization header if token exists
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const res = await axios.post('http://localhost:5000/attack', formData, {
          headers
        });
        data = res.data;
      } else if (selectedImageUrl) {
        // Handle URL-based attack
        const requestData = {
          imageUrl: selectedImageUrl,
          model: selectedModel,
          epsilon: epsilon,
          autoTune: autoTune
        };
        
        // Set up request headers with authentication token
        const headers: any = {
          'Content-Type': 'application/json'
        };
        
        if (token) {
          // Add the Authorization header if token exists
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const res = await axios.post('http://localhost:5000/attack-from-url', requestData, {
          headers
        });
        data = res.data;
      }

      if (data) {
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
      }
    } catch (error) {
      console.error("Error processing attack:", error);
      alert('Error processing attack');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Image Selector Component */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Select Image</h3>
        <ImageSelector onImageSelect={handleImageSelect} />
      </div>

      {/* File Upload */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Or Upload Your Own Image</h3>
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
