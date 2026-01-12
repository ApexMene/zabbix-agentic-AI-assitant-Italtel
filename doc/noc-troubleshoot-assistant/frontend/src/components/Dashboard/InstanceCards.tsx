import { Grid, Card, CardContent, Typography, Box, Chip, LinearProgress } from '@mui/material';
import { CheckCircle, Error, Warning, Router, Cloud } from '@mui/icons-material';
import { useInstanceStore } from '@/stores/instanceStore';

export default function InstanceCards() {
  const { instances, setSelectedInstance, selectedInstanceId } = useInstanceStore();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle sx={{ color: '#4caf50', fontSize: 40 }} />;
      case 'error':
        return <Error sx={{ color: '#f44336', fontSize: 40 }} />;
      default:
        return <Warning sx={{ color: '#757575', fontSize: 40 }} />;
    }
  };

  const getInstanceIcon = (name: string) => {
    if (name.includes('5G') || name.includes('Core')) {
      return <Cloud sx={{ fontSize: 28, color: 'primary.main' }} />;
    }
    return <Router sx={{ fontSize: 28, color: 'primary.main' }} />;
  };

  const handleCardClick = (instanceId: string) => {
    setSelectedInstance(selectedInstanceId === instanceId ? null : instanceId);
  };

  return (
    <Grid container spacing={2}>
      {Array.isArray(instances) && instances.map((instance) => {
        const isSelected = selectedInstanceId === instance.id;
        
        return (
          <Grid item xs={12} sm={6} key={instance.id}>
            <Card
              sx={{
                cursor: 'pointer',
                border: 2,
                borderColor: isSelected ? 'primary.main' : 'transparent',
                bgcolor: isSelected ? 'action.selected' : 'background.paper',
                '&:hover': { 
                  borderColor: 'primary.main',
                  transform: 'translateY(-2px)',
                  transition: 'all 0.2s'
                },
                height: '100%',
              }}
              onClick={() => handleCardClick(instance.id)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getInstanceIcon(instance.name)}
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                        {instance.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {instance.id}
                      </Typography>
                    </Box>
                  </Box>
                  {getStatusIcon(instance.status)}
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Chip
                    label={instance.status.toUpperCase()}
                    size="small"
                    color={instance.status === 'connected' ? 'success' : 'error'}
                    sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}
                  />
                  {instance.version && (
                    <Chip
                      label={`Zabbix ${instance.version}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  )}
                </Box>

                {instance.status === 'connected' && (
                  <Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      MONITORING STATUS
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={100} 
                      sx={{ 
                        height: 6, 
                        borderRadius: 1,
                        bgcolor: 'action.hover',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: '#4caf50'
                        }
                      }} 
                    />
                  </Box>
                )}
                
                {instance.error && (
                  <Box sx={{ mt: 2, p: 1, bgcolor: 'error.dark', borderRadius: 1 }}>
                    <Typography variant="caption" color="error.light" sx={{ wordBreak: 'break-word' }}>
                      {instance.error}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
}
