import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Import the existing CSS
import '../static/index.css';

// Mount the React application
const rootElement = document.getElementById('react-root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}