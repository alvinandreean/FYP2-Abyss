import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Function to check if a JWT token is potentially valid
const validateToken = () => {
  try {
    // For development debugging - uncomment to always start without a token
    // This helps reset the authentication state when testing
    console.log('Checking token validity at startup');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    console.log('Cleared authentication tokens at startup for testing');
    return;
    
    const token = localStorage.getItem('token');
    
    // If there's no token, nothing to validate
    if (!token) return;
    
    // Simple check: token should be a string and have proper JWT structure (xxx.yyy.zzz)
    if (!token.match(/^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/)) {
      console.log('Invalid token format detected, removing');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return;
    }
    
    // Check if token is expired by decoding
    const parts = token.split('.');
    if (parts.length < 2) return;
    
    const payload = JSON.parse(atob(parts[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    
    if (Date.now() >= exp) {
      console.log('Token has expired, removing');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  } catch (e) {
    console.error('Error validating token:', e);
    // If there's any error in validation, clear token to be safe
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

// Validate token before rendering the app
validateToken();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
