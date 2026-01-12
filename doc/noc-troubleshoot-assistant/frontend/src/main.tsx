import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'

console.log('Starting React application...');

try {
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Root element not found');
  }
  
  console.log('Root element found, rendering app...');
  
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
  
  console.log('App rendered successfully');
} catch (error) {
  console.error('Failed to start application:', error);
  const errorMessage = error instanceof Error ? error.message : String(error);
  document.body.innerHTML = `<div style="color: red; padding: 20px;">Error: ${errorMessage}</div>`;
}
