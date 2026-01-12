import { Box, Typography, IconButton, Divider } from '@mui/material';
import { Refresh as RefreshIcon, Circle } from '@mui/icons-material';
import { useEffect, useState } from 'react';
import { useInstanceStore } from '@/stores/instanceStore';
import { api } from '@/services/api';

export default function ConnectionStatusBar() {
  const { instances, setInstances } = useInstanceStore();
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadInstances = async () => {
    setIsRefreshing(true);
    try {
      const data = await api.getInstances();
      setInstances(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load instances:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadInstances();
    const interval = setInterval(loadInstances, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    const color = status === 'connected' ? '#4caf50' : status === 'error' ? '#f44336' : '#757575';
    return <Circle sx={{ fontSize: 12, color, mr: 0.5 }} />;
  };

  return (
    <Box
      sx={{
        bgcolor: '#1e1e1e',
        borderBottom: 2,
        borderColor: 'divider',
        px: 3,
        py: 1.5,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
      }}
    >
      <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 600 }}>
        ZABBIX INSTANCES:
      </Typography>
      
      {Array.isArray(instances) && instances.map((instance, idx) => (
        <Box key={instance.id} sx={{ display: 'flex', alignItems: 'center' }}>
          {idx > 0 && <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {getStatusIcon(instance.status)}
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              {instance.name}
            </Typography>
            {instance.version && (
              <Typography variant="caption" sx={{ ml: 0.5, color: 'text.secondary' }}>
                (v{instance.version})
              </Typography>
            )}
          </Box>
        </Box>
      ))}
      
      <Box sx={{ flexGrow: 1 }} />
      
      {lastUpdate && (
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          Last Update: {lastUpdate.toLocaleTimeString()}
        </Typography>
      )}
      
      <IconButton 
        size="small" 
        onClick={loadInstances}
        disabled={isRefreshing}
        sx={{ 
          color: 'primary.main',
          '&:hover': { bgcolor: 'action.hover' }
        }}
      >
        <RefreshIcon fontSize="small" sx={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }} />
      </IconButton>
      
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </Box>
  );
}
