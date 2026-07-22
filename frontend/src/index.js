import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication, EventType } from '@azure/msal-browser';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import theme from './theme';

// MSAL configuration
const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_AZURE_AD_CLIENT_ID || 'your-client-id',
    authority: `https://login.microsoftonline.com/${process.env.REACT_APP_AZURE_AD_TENANT_ID || 'your-tenant-id'}`,
    redirectUri: process.env.REACT_APP_AZURE_AD_REDIRECT_URI || 'http://localhost:3000',
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

// Initialize MSAL before rendering
async function initializeMsal() {
  try {
    // Handle redirect promise (required for redirect flow)
    await msalInstance.initialize();

    // Handle the redirect response if any
    const response = await msalInstance.handleRedirectPromise().catch((error) => {
      console.warn('MSAL redirect error (can be ignored on first load):', error.message);
      return null;
    });

    if (response) {
      msalInstance.setActiveAccount(response.account);
    }

    // Set active account if available
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      msalInstance.setActiveAccount(accounts[0]);
    }

    // Listen for sign-in events
    msalInstance.addEventCallback((event) => {
      if (event.eventType === EventType.LOGIN_SUCCESS && event.payload?.account) {
        msalInstance.setActiveAccount(event.payload.account);
      }
    });
  } catch (error) {
    console.warn('MSAL initialization error:', error.message);
  }

  // Render the app regardless of MSAL state
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <BrowserRouter>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <App />
          </ThemeProvider>
        </BrowserRouter>
      </MsalProvider>
    </React.StrictMode>
  );
}

initializeMsal();
