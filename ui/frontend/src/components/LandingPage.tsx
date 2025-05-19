import React from 'react';
import { useNavigate } from 'react-router-dom';
import landingBackground from '../assets/abyss.gif';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundImage: `url(${landingBackground})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
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
    </div>
  );
};

export default LandingPage; 