import React from 'react';

interface ModelSelectorProps {
  selectedModel: string;
  setSelectedModel: (model: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ selectedModel, setSelectedModel }) => {
  return (
    <div style={{ marginBottom: '40px' }}>
      <label htmlFor="model-select" style={{ display: 'block', marginBottom: '10px' }}>
        Select Model:
      </label>
      <select
        id="model-select"
        value={selectedModel}
        onChange={(e) => setSelectedModel(e.target.value)}
        style={{
          width: '100%',
          padding: '8px',
          backgroundColor: '#444',
          color: '#fff',
          border: '1px solid #555',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        <option value="mobilenet_v2">MobileNetV2</option>
        <option value="inception_v3">InceptionV3</option>
      </select>
    </div>
  );
};



export default ModelSelector;