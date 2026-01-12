import { Box } from '@mui/material';
import Dashboard from '../Dashboard/Dashboard';
import ChatInterface from '../Chat/ChatInterface';

export default function MainLayout() {
  return (
    <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden', bgcolor: '#121212' }}>
      {/* Main Dashboard Panel */}
      <Box 
        sx={{ 
          flex: 2, 
          overflow: 'auto', 
          p: 3,
          '&::-webkit-scrollbar': { width: 8 },
          '&::-webkit-scrollbar-thumb': { 
            bgcolor: '#555', 
            borderRadius: 4 
          },
        }}
      >
        <Dashboard />
      </Box>
      
      {/* Chat Panel */}
      <Box
        sx={{
          flex: 1,
          minWidth: 450,
          maxWidth: 600,
          borderLeft: 2,
          borderColor: 'divider',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: '#1a1a1a',
        }}
      >
        <ChatInterface />
      </Box>
    </Box>
  );
}
