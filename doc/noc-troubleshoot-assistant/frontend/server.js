import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 13000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:13001';

// Serve static files
app.use(express.static(path.join(__dirname, 'dist')));

// API proxy
app.all('/api/*', async (req, res) => {
  const url = `${BACKEND_URL}${req.url}`;
  try {
    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined,
    });
    const data = await response.json();
    res.status(response.status).json(data);
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
