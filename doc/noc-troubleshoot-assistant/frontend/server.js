import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 13000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:13001';

// Parse JSON bodies
app.use(express.json());

// Debug middleware
app.use((req, res, next) => {
  if (req.method === 'POST') {
    console.log('POST request:', req.url, 'Body:', req.body);
  }
  next();
});

// Serve static files
app.use(express.static(path.join(__dirname, 'dist')));

// Special handling for SSE streaming endpoints (must be GET)
app.get('/api/chat/investigation/:id/stream', async (req, res) => {
  const url = `${BACKEND_URL}/api/chat/investigation/${req.params.id}/stream`;
  
  try {
    const response = await fetch(url);
    
    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // Pipe the stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      res.write(decoder.decode(value));
    }
    res.end();
  } catch (err) {
    console.error('Stream proxy error:', err);
    res.write(`data: ${JSON.stringify({type: 'error', message: err.message})}\n\n`);
    res.end();
  }
});

// API proxy for other endpoints
app.all('/api/*', async (req, res) => {
  const url = `${BACKEND_URL}${req.url}`;
  
  try {
    const options = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    // Add body for POST/PUT/PATCH
    if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
      options.body = JSON.stringify(req.body);
    }
    
    const response = await fetch(url, options);
    
    // Handle streaming responses (SSE)
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('text/event-stream')) {
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        res.write(decoder.decode(value));
      }
      res.end();
    } else {
      // Regular JSON response
      const data = await response.json();
      res.status(response.status).json(data);
    }
  } catch (err) {
    console.error('API proxy error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Health proxy
app.get('/health', async (req, res) => {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Serve index.html for all other routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend server running on http://0.0.0.0:${PORT}`);
  console.log(`Backend URL: ${BACKEND_URL}`);
});
