import { Box, Paper, Typography, Divider } from '@mui/material';
import { Psychology } from '@mui/icons-material';

export default function ChatInterface() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', bgcolor: '#1a1a1a' }}>
      {/* Chat Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            AI Investigation Assistant
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          Powered by Amazon Bedrock
        </Typography>
      </Box>
      
      {/* Chat Content */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Paper
          sx={{
            p: 4,
            textAlign: 'center',
            bgcolor: 'background.paper',
            maxWidth: 400,
          }}
        >
          <Psychology sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Ready to Investigate
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click the <strong>Investigate</strong> button on any alarm to start AI-powered root cause analysis
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Typography variant="caption" color="text.secondary">
            The AI assistant will automatically:
          </Typography>
          <Box component="ul" sx={{ textAlign: 'left', mt: 1, pl: 2 }}>
            <Typography component="li" variant="caption" color="text.secondary">
              Query Zabbix for host metrics
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              Analyze historical data
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              Provide root cause analysis
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              Suggest remediation steps
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
}
