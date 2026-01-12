import { AppBar, Toolbar, Typography, Box, Chip } from '@mui/material';
import { NetworkCheck, Security } from '@mui/icons-material';

export default function Header() {
  return (
    <AppBar position="static" elevation={2} sx={{ bgcolor: '#1a1a1a' }}>
      <Toolbar>
        <NetworkCheck sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
          Network Operations Center
        </Typography>
        <Box sx={{ mx: 2 }}>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            AI-Powered Troubleshooting
          </Typography>
        </Box>
        <Box sx={{ flexGrow: 1 }} />
        <Chip
          icon={<Security />}
          label="SOC MONITORING"
          color="primary"
          size="small"
          sx={{ fontWeight: 'bold' }}
        />
      </Toolbar>
    </AppBar>
  );
}
