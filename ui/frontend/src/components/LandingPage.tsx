import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  
  const clearLocalStorage = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    console.log('Cleared localStorage tokens');
    window.dispatchEvent(new Event('auth-change'));
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#222',
      color: 'white',
      padding: '20px',
      textAlign: 'center'
    }}>
      <h1 style={{ 
        fontSize: '5rem', 
        marginBottom: '1rem',
        textShadow: '2px 2px 4px rgba(0, 0, 0, 0.5)'
      }}>
        ABYSS
      </h1>
      
      <p style={{ 
        fontSize: '1.5rem', 
        marginBottom: '3rem',
        fontStyle: 'italic'
      }}>
        AI: meets the dark side
      </p>
      
      <div style={{
        display: 'flex',
        gap: '20px'
      }}>
        <button 
          onClick={() => navigate('/login')} 
          style={{ 
            fontSize: '1.2rem',
            padding: '12px 28px',
            backgroundColor: '#646cff',
            color: 'white'
          }}
        >
          Login
        </button>
        
        <button 
          onClick={() => navigate('/register')} 
          style={{ 
            fontSize: '1.2rem',
            padding: '12px 28px',
            backgroundColor: '#1a1a1a',
            color: 'white'
          }}
        >
          Register
        </button>
      </div>
      
      {/* Dev button for testing */}
      <button 
        onClick={clearLocalStorage} 
        style={{ 
          marginTop: '20px',
          backgroundColor: 'red',
          padding: '5px 10px',
          fontSize: '0.8rem'
        }}
      >
        Dev: Clear Token
      </button>
    </div>
  );
};

export default LandingPage; 