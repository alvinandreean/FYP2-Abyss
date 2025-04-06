import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';

const App: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [attackInfo, setAttackInfo] = useState<any>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('http://localhost:5000/attack', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setAttackInfo(response.data);
      setResultImage(`data:image/png;base64,${response.data.result_image}`);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>FGSM Adversarial Attack</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit">Run Attack</button>
      </form>
      {attackInfo && (
        <div>
          <p>Epsilon: {attackInfo.epsilon}</p>
          <p>Original Class: {attackInfo.original_class}</p>
          <p>Adversarial Class: {attackInfo.adversarial_class}</p>
        </div>
      )}
      {resultImage && (
        <div>
          <img src={resultImage} alt="Attack Result" style={{ maxWidth: '80%' }} />
        </div>
      )}
    </div>
  );
};

export default App;
