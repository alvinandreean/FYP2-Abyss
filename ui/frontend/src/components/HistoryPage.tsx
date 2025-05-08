import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './Navbar';

interface AttackHistoryItem {
  id: number;
  model_used: string;
  epsilon_used: number;
  orig_class: string;
  orig_conf: number;
  adv_class: string;
  adv_conf: number;
  created_at: string;
}

const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<AttackHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setError('Authentication required');
          setIsLoading(false);
          return;
        }

        const response = await axios.get('http://localhost:5000/history', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.data.success) {
          setHistory(response.data.history);
        } else {
          setError('Failed to load history');
        }
      } catch (err) {
        setError('Error fetching history');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        minHeight: '100vh',
        backgroundColor: '#222',
        color: '#fff'
      }}
    >
      <Navbar />
      
      <div style={{ padding: '20px' }}>
        <h1>Attack History</h1>
        
        {isLoading ? (
          <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <p>Loading history...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', marginTop: '50px', color: '#ff6b6b' }}>
            <p>{error}</p>
          </div>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <p>No attack history found. Try running some attacks first.</p>
          </div>
        ) : (
          <div>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                marginTop: '20px',
                backgroundColor: '#333',
                borderRadius: '8px',
                overflow: 'hidden'
              }}
            >
              <thead>
                <tr>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Date</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Model</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Epsilon</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Original Class</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Confidence</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Adversarial Class</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id} style={{ borderBottom: '1px solid #444' }}>
                    <td style={{ padding: '12px' }}>{formatDate(item.created_at)}</td>
                    <td style={{ padding: '12px' }}>{item.model_used}</td>
                    <td style={{ padding: '12px' }}>{item.epsilon_used.toFixed(5)}</td>
                    <td style={{ padding: '12px' }}>{item.orig_class}</td>
                    <td style={{ padding: '12px' }}>{(item.orig_conf * 100).toFixed(2)}%</td>
                    <td style={{ padding: '12px' }}>{item.adv_class}</td>
                    <td style={{ padding: '12px' }}>{(item.adv_conf * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage; 