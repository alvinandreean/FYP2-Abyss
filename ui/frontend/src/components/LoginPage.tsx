import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import registerBackground from '../assets/abyss.gif';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  
  // Check on component mount if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      console.log('User already has token, redirecting to attack page');
      navigate('/attack', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Form validation
    if (!email || !password) {
      setError('Email and password are required');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Replace with your actual API endpoint
      const response = await axios.post('http://localhost:5000/login', {
        email,
        password
      });
      
      // Store the token in localStorage
      localStorage.setItem('token', response.data.token);
      
      // Store user info in localStorage
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      console.log("Login successful");
      
      // Dispatch a single auth change event
      window.dispatchEvent(new Event('auth-change'));
      
      // Navigate to attack page after login
      navigate('/attack', { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        backgroundImage: `url(${registerBackground})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        color: '#fff',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '20px',
        boxSizing: 'border-box'
      }}
    >
      <div
        style={{
          width: '400px',
          backgroundColor: '#2C3539', // Charcoal gray with cool tone
          padding: '30px',
          borderRadius: '8px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.4)'
        }}
      >
        <h2 style={{ marginBottom: '20px', textAlign: 'center' }}>Login</h2>
        
        {error && (
          <div
            style={{
              backgroundColor: 'rgba(255, 0, 0, 0.1)',
              color: '#ff6b6b',
              padding: '10px',
              borderRadius: '4px',
              marginBottom: '20px',
              textAlign: 'center'
            }}
          >
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label
              htmlFor="email"
              style={{ display: 'block', marginBottom: '8px' }}
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: '#444',
                color: '#fff',
                border: '1px solid #555',
                borderRadius: '4px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          
          <div style={{ marginBottom: '30px' }}>
            <label
              htmlFor="password"
              style={{ display: 'block', marginBottom: '8px' }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: '#444',
                color: '#fff',
                border: '1px solid #555',
                borderRadius: '4px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#4a90e2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1
            }}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          Don't have an account?{' '}
          <a
            href="/register"
            style={{ color: '#4a90e2', textDecoration: 'none' }}
            onClick={(e) => {
              e.preventDefault();
              navigate('/register');
            }}
          >
            Register
          </a>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 