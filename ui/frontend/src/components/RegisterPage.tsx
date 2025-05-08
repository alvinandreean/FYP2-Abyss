import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
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
    if (!email || !password || !confirmPassword || !firstName || !lastName) {
      setError('All fields are required');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Replace with your actual API endpoint
      await axios.post('http://localhost:5000/register', {
        email,
        password,
        user_fname: firstName,
        user_lname: lastName
      });
      
      // Redirect to login page after successful registration
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        backgroundColor: '#222',
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
          backgroundColor: '#333',
          padding: '30px',
          borderRadius: '8px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)'
        }}
      >
        <h2 style={{ marginBottom: '20px', textAlign: 'center' }}>Register</h2>
        
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
              htmlFor="firstName"
              style={{ display: 'block', marginBottom: '8px' }}
            >
              First Name
            </label>
            <input
              id="firstName"
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
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
          
          <div style={{ marginBottom: '20px' }}>
            <label
              htmlFor="lastName"
              style={{ display: 'block', marginBottom: '8px' }}
            >
              Last Name
            </label>
            <input
              id="lastName"
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
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
          
          <div style={{ marginBottom: '20px' }}>
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
          
          <div style={{ marginBottom: '30px' }}>
            <label
              htmlFor="confirmPassword"
              style={{ display: 'block', marginBottom: '8px' }}
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
            {isLoading ? 'Registering...' : 'Register'}
          </button>
        </form>
        
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          Already have an account?{' '}
          <a
            href="/login"
            style={{ color: '#4a90e2', textDecoration: 'none' }}
            onClick={(e) => {
              e.preventDefault();
              navigate('/login');
            }}
          >
            Login
          </a>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
