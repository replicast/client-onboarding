import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useIsAuthenticated } from '@azure/msal-react';
import Layout from './components/common/Layout';
import ClientList from './components/clients/ClientList';
import ClientForm from './components/clients/ClientForm';
import SiteList from './components/sites/SiteList';
import SiteForm from './components/sites/SiteForm';
import { Box, CircularProgress, Typography } from '@mui/material';

// Protected route wrapper
function ProtectedRoute({ children }) {
  const isAuthenticated = useIsAuthenticated();

  if (!isAuthenticated) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <Typography variant="h5">Please sign in to continue</Typography>
        <Typography variant="body2" color="text.secondary">
          Use the Sign In button in the navigation bar
        </Typography>
      </Box>
    );
  }

  return children;
}

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/clients" replace />} />

        <Route
          path="/clients"
          element={
            <ProtectedRoute>
              <ClientList />
            </ProtectedRoute>
          }
        />

        <Route
          path="/clients/new"
          element={
            <ProtectedRoute>
              <ClientForm />
            </ProtectedRoute>
          }
        />

        <Route
          path="/clients/:id"
          element={
            <ProtectedRoute>
              <ClientForm />
            </ProtectedRoute>
          }
        />

        <Route
          path="/clients/:clientId/sites"
          element={
            <ProtectedRoute>
              <SiteList />
            </ProtectedRoute>
          }
        />

        <Route
          path="/clients/:clientId/sites/new"
          element={
            <ProtectedRoute>
              <SiteForm />
            </ProtectedRoute>
          }
        />

        <Route
          path="/clients/:clientId/sites/:id"
          element={
            <ProtectedRoute>
              <SiteForm />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/clients" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
