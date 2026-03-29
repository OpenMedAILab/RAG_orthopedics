import React, { useState, useEffect, useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { StoreContext } from './contexts/StoreContext';
import appStore from './utils/store';
import RatingSystem from './components/RatingSystem';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#e57373',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#f5f7fa',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [storeState, setStoreState] = useState(appStore.getState());

  useEffect(() => {
    // Subscribe to store updates
    const unsubscribe = appStore.subscribe((newState) => {
      setStoreState({ ...newState });
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  // Memoize the context value to prevent unnecessary re-renders
  const storeContextValue = useMemo(() => ({
    state: storeState,
    dispatch: (action, payload) => appStore.setState({ [action]: payload })
  }), [storeState]);

  return (
    <StoreContext.Provider value={storeContextValue}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <RatingSystem />
      </ThemeProvider>
    </StoreContext.Provider>
  );
}

export default App;