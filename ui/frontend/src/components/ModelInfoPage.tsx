import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';

interface ModelMetrics {
  model_name: string;
  architecture: string;
  accuracy: number;
  misclassification_success_rate: number;
  parameters: number;
  training_dataset: string;
  description: string;
}

// Simple visual representation of model architectures
const ModelArchitectureVisual: React.FC<{ modelName: string }> = ({ modelName }) => {
  // Different visuals based on model type
  const getModelVisual = () => {
    switch(modelName) {
      case 'MobileNet V2':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '1rem' }}>
            <div style={{ display: 'flex', gap: '4px', marginBottom: '8px' }}>
              {[...Array(3)].map((_, i) => (
                <div key={i} style={{ width: '30px', height: '30px', backgroundColor: '#61dafb', borderRadius: '4px' }} />
              ))}
            </div>
            <div style={{ width: '100px', height: '2px', backgroundColor: '#555' }} />
            <div style={{ display: 'flex', gap: '4px', margin: '8px 0' }}>
              {[...Array(5)].map((_, i) => (
                <div key={i} style={{ width: '20px', height: '20px', backgroundColor: '#2196f3', borderRadius: '4px' }} />
              ))}
            </div>
            <div style={{ width: '100px', height: '2px', backgroundColor: '#555' }} />
            <div style={{ display: 'flex', gap: '4px', margin: '8px 0' }}>
              {[...Array(7)].map((_, i) => (
                <div key={i} style={{ width: '15px', height: '15px', backgroundColor: '#00bcd4', borderRadius: '4px' }} />
              ))}
            </div>
            <div style={{ width: '100px', height: '2px', backgroundColor: '#555' }} />
            <div style={{ width: '80px', height: '25px', backgroundColor: '#4caf50', borderRadius: '4px' }} />
          </div>
        );
      case 'Inception V3':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '1rem' }}>
            <div style={{ width: '30px', height: '30px', backgroundColor: '#673ab7', borderRadius: '4px', marginBottom: '8px' }} />
            <div style={{ width: '100px', height: '2px', backgroundColor: '#555' }} />
            
            {/* Inception module representation */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', margin: '10px 0' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#3f51b5', borderRadius: '4px' }} />
                <div style={{ width: '2px', height: '20px', backgroundColor: '#555' }} />
                <div style={{ width: '20px', height: '20px', backgroundColor: '#2196f3', borderRadius: '4px' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#3f51b5', borderRadius: '4px' }} />
                <div style={{ width: '2px', height: '20px', backgroundColor: '#555' }} />
                <div style={{ width: '20px', height: '20px', backgroundColor: '#03a9f4', borderRadius: '4px' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ width: '20px', height: '20px', backgroundColor: '#3f51b5', borderRadius: '4px' }} />
                <div style={{ width: '2px', height: '20px', backgroundColor: '#555' }} />
                <div style={{ width: '20px', height: '20px', backgroundColor: '#00bcd4', borderRadius: '4px' }} />
              </div>
            </div>
            
            <div style={{ width: '100px', height: '2px', backgroundColor: '#555' }} />
            <div style={{ width: '80px', height: '25px', backgroundColor: '#4caf50', borderRadius: '4px', marginTop: '10px' }} />
          </div>
        );
      default:
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '1rem' }}>
            <div style={{ width: '50px', height: '50px', backgroundColor: '#607d8b', borderRadius: '4px' }} />
            <div style={{ width: '2px', height: '20px', backgroundColor: '#555' }} />
            <div style={{ width: '80px', height: '25px', backgroundColor: '#4caf50', borderRadius: '4px' }} />
          </div>
        );
    }
  };

  return (
    <div style={{ 
      border: '1px solid #444', 
      borderRadius: '8px', 
      padding: '1rem',
      marginTop: '1rem',
      backgroundColor: '#2a2a2a'
    }}>
      <h4 style={{ textAlign: 'center', marginBottom: '1rem', color: '#61dafb' }}>Architecture Visualization</h4>
      {getModelVisual()}
    </div>
  );
};

const ModelInfoPage: React.FC = () => {
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        console.log('Fetching model info...');
        
        // Use the API path that works with the Nginx proxy in Docker
        const apiUrl = '/api/model-info';
        
        console.log('Using API URL:', apiUrl);
        const response = await fetch(apiUrl);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch model information: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Model info data received:', data);
        setModelMetrics(data);
      } catch (err) {
        console.error('Error fetching model info:', err);
        setError(`Error loading model information: ${err instanceof Error ? err.message : String(err)}`);
      } finally {
        setLoading(false);
      }
    };

    fetchModelInfo();
  }, []);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#222', color: '#fff' }}>
      <Navbar />
      <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '2rem', borderBottom: '1px solid #444', paddingBottom: '0.5rem' }}>
          Model Information & Quality Metrics
        </h1>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>Loading model information...</div>
        ) : error ? (
          <div style={{ color: '#ff6b6b', padding: '1rem', border: '1px solid #ff6b6b', borderRadius: '4px' }}>
            {error}
          </div>
        ) : (
          <div>
            {modelMetrics.map((model, index) => (
              <div 
                key={index} 
                style={{ 
                  backgroundColor: '#333', 
                  borderRadius: '8px', 
                  padding: '1.5rem', 
                  marginBottom: '2rem',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                }}
              >
                <h2 style={{ color: '#61dafb', marginBottom: '1rem' }}>{model.model_name}</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                  {/* Model Architecture Section */}
                  <div>
                    <h3 style={{ borderBottom: '1px solid #444', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                      Model Architecture
                    </h3>
                    <div style={{ marginBottom: '1rem' }}>
                      <strong>Type:</strong> {model.architecture}
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <strong>Parameters:</strong> {model.parameters.toLocaleString()}
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <strong>Training Dataset:</strong> {model.training_dataset}
                    </div>
                    <div>
                      <strong>Description:</strong>
                      <p style={{ lineHeight: '1.6' }}>{model.description}</p>
                    </div>
                    
                    {/* Add the visual representation */}
                    <ModelArchitectureVisual modelName={model.model_name} />
                  </div>
                  
                  {/* Quality Metrics Section */}
                  <div>
                    <h3 style={{ borderBottom: '1px solid #444', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                      Quality Metrics
                    </h3>
                    
                    <div style={{ marginBottom: '2rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <strong>Model Accuracy:</strong>
                        <span>{(model.accuracy * 100).toFixed(2)}%</span>
                      </div>
                      <div style={{ width: '100%', backgroundColor: '#444', borderRadius: '4px', height: '10px' }}>
                        <div 
                          style={{ 
                            width: `${model.accuracy * 100}%`, 
                            backgroundColor: '#4caf50', 
                            height: '100%', 
                            borderRadius: '4px' 
                          }} 
                        />
                      </div>
                    </div>
                    
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <strong>Misclassification Success Rate:</strong>
                        <span>{(model.misclassification_success_rate * 100).toFixed(2)}%</span>
                      </div>
                      <div style={{ width: '100%', backgroundColor: '#444', borderRadius: '4px', height: '10px' }}>
                        <div 
                          style={{ 
                            width: `${model.misclassification_success_rate * 100}%`, 
                            backgroundColor: '#ff9800', 
                            height: '100%', 
                            borderRadius: '4px' 
                          }} 
                        />
                      </div>
                      <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#ccc' }}>
                        <p><em>Misclassification Success Rate: The rate at which adversarial attacks successfully cause the model to misclassify images.</em></p>
                      </div>
                    </div>

                    {/* Additional metrics visualization */}
                    <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#2a2a2a', borderRadius: '8px' }}>
                      <h4 style={{ marginBottom: '1rem', color: '#61dafb' }}>Performance Comparison</h4>
                      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
                        <div style={{ width: '120px' }}>Accuracy</div>
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                          <div style={{ 
                            width: `${model.accuracy * 100}%`, 
                            backgroundColor: '#4caf50', 
                            height: '20px', 
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'flex-end',
                            paddingRight: '8px',
                            color: '#fff',
                            fontWeight: 'bold',
                            fontSize: '0.8rem'
                          }}>
                            {(model.accuracy * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <div style={{ width: '120px' }}>Vulnerability</div>
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                          <div style={{ 
                            width: `${model.misclassification_success_rate * 100}%`, 
                            backgroundColor: '#ff9800', 
                            height: '20px', 
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'flex-end',
                            paddingRight: '8px',
                            color: '#fff',
                            fontWeight: 'bold',
                            fontSize: '0.8rem'
                          }}>
                            {(model.misclassification_success_rate * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelInfoPage; 