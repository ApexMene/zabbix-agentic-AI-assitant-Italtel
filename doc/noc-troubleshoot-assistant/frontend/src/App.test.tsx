import { ThemeProvider, CssBaseline, Box, Typography } from '@mui/material';
import { darkTheme } from './theme/darkTheme';

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ p: 4 }}>
        <Typography variant="h4" color="primary">
          Network Troubleshooting Assistant
        </Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading application...
        </Typography>
      </Box>
    </ThemeProvider>
  );
}

export default App;
