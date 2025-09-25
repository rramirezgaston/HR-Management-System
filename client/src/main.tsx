import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Import the MUI components
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Create a simple theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Wrap the App in the ThemeProvider */}
    <ThemeProvider theme={darkTheme}>
      {/* CssBaseline provides a consistent styling baseline */}
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);