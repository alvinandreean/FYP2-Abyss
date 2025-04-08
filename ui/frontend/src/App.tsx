import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AttackPage from './components/FirstPage';
import ResultsPage from './components/ResultsPage';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Attack form page */}
        <Route path="/" element={<AttackPage />} />
        {/* Results page */}
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
};

export default App;
