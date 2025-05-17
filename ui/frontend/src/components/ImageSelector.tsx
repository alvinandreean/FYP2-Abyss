import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Image {
  filename: string;
  label: string;
  url: string;
}

interface ImageSelectorProps {
  onImageSelect: (imageUrl: string) => void;
}

const ImageSelector: React.FC<ImageSelectorProps> = ({ onImageSelect }) => {
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showSelector, setShowSelector] = useState<boolean>(false);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await axios.get('http://localhost:5000/available-images');
        if (response.data.success) {
          setImages(response.data.images);
        } else {
          setError('Failed to load images');
        }
      } catch (err) {
        setError('Error connecting to server');
        console.error('Error fetching images:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, []);

  const handleImageSelect = (url: string) => {
    onImageSelect(url);
    setShowSelector(false);
  };

  return (
    <div style={{ marginBottom: '20px' }}>
      <button
        onClick={() => setShowSelector(!showSelector)}
        style={{
          padding: '8px 12px',
          backgroundColor: '#4a90e2',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '10px'
        }}
      >
        {showSelector ? 'Hide Available Images' : 'Choose from Available Images'}
      </button>

      {showSelector && (
        <div style={{ 
          backgroundColor: '#444',
          padding: '15px',
          borderRadius: '4px',
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          {loading && <p>Loading images...</p>}
          
          {error && <p style={{ color: '#ff6b6b' }}>{error}</p>}
          
          {!loading && !error && images.length === 0 && (
            <p>No images available</p>
          )}
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
            gap: '10px' 
          }}>
            {images.map((image, index) => (
              <div 
                key={index}
                onClick={() => handleImageSelect(image.url)}
                style={{ 
                  cursor: 'pointer',
                  textAlign: 'center',
                  padding: '8px',
                  backgroundColor: '#333',
                  borderRadius: '4px',
                  transition: 'transform 0.2s',
                  ':hover': {
                    transform: 'scale(1.05)'
                  }
                }}
              >
                <img 
                  src={image.url} 
                  alt={image.label}
                  style={{ 
                    width: '100%', 
                    height: '100px', 
                    objectFit: 'cover',
                    borderRadius: '4px'
                  }}
                />
                <p style={{ 
                  margin: '5px 0 0 0',
                  fontSize: '12px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {image.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageSelector; 