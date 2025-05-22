import React from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    console.log("Logging out...");
    
    // Remove auth data from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Dispatch event to notify auth change
    window.dispatchEvent(new Event('auth-change'));
    
    // Navigate to login page directly with replace to prevent back navigation
    navigate('/login', { replace: true });
  };
  
  return (
    <nav
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#333',
        color: '#fff',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
      }}
    >
      <div
        style={{
          fontWeight: 'bold',
          fontSize: '1.2rem',
          cursor: 'pointer'
        }}
        onClick={() => navigate('/attack')}
      >
        Adversarial Attack Demo
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div
          style={{
            marginRight: '20px',
            cursor: 'pointer',
            padding: '8px 12px',
            borderRadius: '4px',
            transition: 'background-color 0.3s ease'
          }}
          onClick={() => navigate('/attack')}
        >
          Attack
        </div>
        
        <div
          style={{
            marginRight: '20px',
            cursor: 'pointer',
            padding: '8px 12px',
            borderRadius: '4px',
            transition: 'background-color 0.3s ease'
          }}
          onClick={() => navigate('/history')}
        >
          History
        </div>

        <div
          style={{
            marginRight: '20px',
            cursor: 'pointer',
            padding: '8px 12px',
            borderRadius: '4px',
            transition: 'background-color 0.3s ease'
          }}
          onClick={() => navigate('/model-info')}
        >
          Model Info
        </div>
        
        <button
          onClick={handleLogout}
          style={{
            backgroundColor: 'transparent',
            border: '1px solid #fff',
            color: '#fff',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar; 