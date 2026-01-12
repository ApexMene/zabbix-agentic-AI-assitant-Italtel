# Frontend Troubleshooting

## White Screen Issue

If you see a white screen when accessing http://localhost:13000:

### Solution 1: Hard Refresh
- **Mac**: `Cmd + Shift + R`
- **Windows/Linux**: `Ctrl + Shift + R`

### Solution 2: Clear Cache
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Solution 3: Incognito Mode
Open http://localhost:13000 in an incognito/private window

### Solution 4: Check Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for JavaScript errors
4. Check Network tab for failed requests

## Verify Frontend is Working

```bash
# Check if server is running
curl http://localhost:13000

# Check if API proxy works
curl http://localhost:13000/health

# Check if alarms are accessible
curl http://localhost:13000/api/alarms
```

All should return valid responses.

## Development Mode

For development with hot reload:

```bash
cd frontend
npm run dev
```

This starts Vite dev server on http://localhost:13003 (or next available port).
