# Client Onboarding - Frontend

React frontend for the Client Onboarding application with Material-UI and Azure Maps integration.

## Features

- **Client Management**: List, search, create, edit, and delete clients
- **Site Management**: Manage sites for each client with geolocation polygons
- **Azure Maps Integration**: Draw and edit geolocation polygons on interactive maps
- **Azure AD Authentication**: Secure login using Microsoft Azure AD
- **Material-UI**: Modern, responsive UI components

## Tech Stack

- **React 18**: Modern React with hooks
- **Material-UI (MUI)**: Comprehensive component library
- **Azure Maps**: Interactive maps with drawing tools
- **MSAL React**: Microsoft Authentication Library for Azure AD
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

## Prerequisites

- Node.js 16+ and npm
- Backend API running (see `/backend` directory)
- Azure AD app registration
- Azure Maps subscription key

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

## Configuration

Edit `.env` file with your credentials:

```env
# Backend API
REACT_APP_API_URL=http://localhost:8000/api

# Azure AD
REACT_APP_AZURE_AD_CLIENT_ID=your-client-id
REACT_APP_AZURE_AD_TENANT_ID=your-tenant-id
REACT_APP_AZURE_AD_REDIRECT_URI=http://localhost:3000

# Azure Maps
REACT_APP_AZURE_MAPS_KEY=your-azure-maps-key
```

## Running the Application

### Development

```bash
npm start
```

The app will open at http://localhost:3000

### Production Build

```bash
npm run build
```

Build output will be in the `build/` directory.

## Project Structure

```
src/
├── components/
│   ├── clients/        # Client management components
│   ├── sites/          # Site management components
│   ├── common/         # Shared components (Layout, Navigation)
│   └── auth/           # Authentication components
├── services/           # API service layer
│   ├── api.js          # Axios instance with auth interceptor
│   ├── clientService.js
│   └── siteService.js
├── contexts/           # React contexts
├── App.jsx             # Main app component with routing
├── index.js            # App entry point
└── theme.js            # Material-UI theme configuration
```

## Features

### Client Management
- List all clients with search/filter
- Create new clients
- Edit existing clients
- Delete clients (with cascade delete of sites)
- View client details with associated sites

### Site Management
- View all sites for a client
- Create new sites with geolocation polygons
- Edit site details and polygons
- Delete sites
- Interactive Azure Maps for drawing polygons

### Authentication
- Azure AD SSO login
- Protected routes
- Automatic token management
- Sign in/sign out functionality

## Azure Maps Integration

The application uses Azure Maps for drawing and editing geolocation polygons:

- **Drawing Tools**: Polygon drawing on interactive maps
- **GeoJSON Support**: Polygons stored in GeoJSON format
- **Edit Mode**: Edit existing polygons
- **Visualization**: Display site polygons on map

## API Integration

All API calls use Axios with:
- Automatic authentication header injection
- Error handling
- Base URL configuration
- Request/response interceptors

## Development Notes

- MSAL handles Azure AD authentication
- Protected routes require authentication
- API tokens automatically added to requests
- Environment variables must start with `REACT_APP_`
- Material-UI theme customizable in `theme.js`

## License

Private - All Rights Reserved
