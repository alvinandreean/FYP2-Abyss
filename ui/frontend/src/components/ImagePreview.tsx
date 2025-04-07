import React from 'react';

interface ImagePreviewProps {
  preview: string;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ preview }) => {
  return (
    <div style={{ marginTop: '60px', textAlign: 'center' }}>
      <h3>Image Preview</h3>
      <img
        src={preview}
        alt="Preview"
        style={{
          maxWidth: '100%',
          border: '2px solid #444',
          borderRadius: '4px'
        }}
      />
    </div>
  );
};

export default ImagePreview;