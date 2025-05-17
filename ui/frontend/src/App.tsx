import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AttackPage from './components/FirstPage';
import ResultsPage from './components/ResultsPage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import HistoryPage from './components/HistoryPage';
import LandingPage from './components/LandingPage';

// Create a wrapper component to handle authentication
const AuthWrapper: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [authChecked, setAuthChecked] = useState<boolean>(false);

  // Check for token on mount and whenever the location changes
  const checkAuth = useCallback(() => {
    const token = localStorage.getItem('token');
    console.log('DEBUG - Auth check - Token exists:', !!token, 'Token value:', token?.substring(0, 10) + '...');
    const newAuthState = !!token;
    
    // Only log and update state if there's a change or first check
    if (!authChecked || isAuthenticated !== newAuthState) {
      console.log('Auth check: Token exists?', newAuthState);
      setIsAuthenticated(newAuthState);
    }
    
    setAuthChecked(true);
    setIsLoading(false);
  }, [isAuthenticated, authChecked]);
  
  // Check auth whenever the component mounts
  useEffect(() => {
    // Immediately check auth on component mount
    checkAuth();
    
    // Set up event listener for storage changes
    const handleStorageChange = () => {
      checkAuth();
    };
    
    // Create a custom event for auth changes within the same window
    const handleAuthChange = () => {
      console.log('Auth change event triggered');
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth-change', handleAuthChange);
    
    // Recheck auth, but less frequently to avoid excessive renders
    const interval = setInterval(checkAuth, 3000);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-change', handleAuthChange);
      clearInterval(interval);
    };
  }, [checkAuth]);

  // Protected route component
  const ProtectedRoute: React.FC<{ element: React.ReactElement }> = ({ element }) => {
    // Only log when the auth state changes to reduce console spam
    if (!isLoading && authChecked) {
      console.log('Protected route check, isAuthenticated:', isAuthenticated);
    }
    
    if (isLoading) {
      return <div style={{ padding: '20px', color: '#fff', backgroundColor: '#222', minHeight: '100vh' }}>Loading...</div>;
    }
    
    // Force a re-check of authentication before making a decision
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No token found, redirecting to login');
      return <Navigate to="/login" />;
    }
    
    return element;
  };
  
  // Provide the authentication state and ProtectedRoute to children
  return (
    <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, isLoading, ProtectedRoute }}>
      {children}
    </AuthContext.Provider>
  );
};

// Create a context to share authentication state
const AuthContext = React.createContext<{
  isAuthenticated: boolean;
  setIsAuthenticated: React.Dispatch<React.SetStateAction<boolean>>;
  isLoading: boolean;
  ProtectedRoute: React.FC<{ element: React.ReactElement }>;
}>({
  isAuthenticated: false,
  setIsAuthenticated: () => {},
  isLoading: true,
  ProtectedRoute: () => <></>,
});

// Root component that shows loading until initial auth check is complete
const AppRouter: React.FC = () => {
  // Access auth context values
  const { isAuthenticated, isLoading } = React.useContext(AuthContext);
  
  if (isLoading) {
    return <div style={{ padding: '20px', color: '#fff', backgroundColor: '#222', minHeight: '100vh' }}>
      Checking authentication...
    </div>;
  }
  
  // For testing purposes - uncomment to always show the landing page
  const isDevelopmentTesting = true;
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/attack" /> : <LoginPage />
      } />
      <Route path="/register" element={
        isAuthenticated ? <Navigate to="/attack" /> : <RegisterPage />
      } />
      
      {/* Root path shows landing page, or attack page if authenticated */}
      <Route path="/" element={
        isDevelopmentTesting ? <LandingPage /> : 
        (isAuthenticated ? <Navigate to="/attack" /> : <LandingPage />)
      } />
      
      {/* Protected routes - using the AuthContext consumer */}
      <Route path="/attack" element={
        <AuthContext.Consumer>
          {({ ProtectedRoute }) => <ProtectedRoute element={<AttackPage />} />}
        </AuthContext.Consumer>
      } />
      <Route path="/results" element={
        <AuthContext.Consumer>
          {({ ProtectedRoute }) => <ProtectedRoute element={<ResultsPage />} />}
        </AuthContext.Consumer>
      } />
      <Route path="/history" element={
        <AuthContext.Consumer>
          {({ ProtectedRoute }) => <ProtectedRoute element={<HistoryPage />} />}
        </AuthContext.Consumer>
      } />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthWrapper>
        <AppRouter />
      </AuthWrapper>
    </Router>
  );
};

export default App;
