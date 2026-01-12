import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { darkTheme } from './theme/darkTheme';
import Header from './components/Layout/Header';
import ConnectionStatusBar from './components/Layout/ConnectionStatusBar';
import MainLayout from './components/Layout/MainLayout';

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        <Header />
        <ConnectionStatusBar />
        <MainLayout />
      </Box>
    </ThemeProvider>
  );
}

export default App;
