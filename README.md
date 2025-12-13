# Client Onboarding Application

Full-stack web application for client onboarding and site management with geolocation support.

## Overview

This application enables organizations to onboard clients and manage their sites with geolocation data. It features a React frontend with Material-UI, a FastAPI Python backend, Azure SQL Database for storage, and Azure AD for authentication.

## Architecture

- **Frontend**: React + Material-UI + Azure Maps
- **Backend**: FastAPI (Python) - all API endpoints
- **Database**: Azure SQL Database with spatial data support
- **Authentication**: Azure AD / Entra ID
- **Maps**: Azure Maps for polygon drawing

**Important**: Node.js is only used for React development tools. All backend APIs are FastAPI (Python).

## Features

### Client Management
- Create, read, update, delete clients
- Search and filter clients
- Track client attributes:
  - Client name
  - Country
  - Business type
  - Organization size

### Site Management
- Manage multiple sites per client
- Draw geolocation polygons on interactive maps
- Site attributes:
  - Site name
  - Geolocation polygon (GeoJSON)
  - Site type

### Security
- Azure AD Single Sign-On (SSO)
- Protected API endpoints
- JWT token validation
- Role-based access (future enhancement)

## Project Structure

```
client-onboarding/
├── backend/                    # FastAPI backend (Python)
│   ├── app/
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── auth/              # Azure AD authentication
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   ├── .env.example
│   └── README.md
├── .gitignore
└── README.md
```

## Prerequisites

### Backend
- Python 3.11+
- Azure SQL Database
- Azure AD tenant and app registration
- ODBC Driver 18 for SQL Server

### Frontend
- Node.js 16+
- npm or yarn
- Azure AD app registration (same or separate from backend)
- Azure Maps subscription key

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# Run the app
npm start
```

Frontend will be available at: http://localhost:3000

## Configuration

### Azure SQL Database

1. Create an Azure SQL Database instance
2. Note the server name, database name, and credentials
3. Add connection details to `backend/.env`

### Azure AD Setup

1. Register an app in Azure AD (Azure Portal > App Registrations)
2. Note the Tenant ID and Client ID
3. Create a client secret
4. Add redirect URI: `http://localhost:3000` (for frontend)
5. Add API permissions (if needed)
6. Add credentials to both `backend/.env` and `frontend/.env`

### Azure Maps

1. Create an Azure Maps account (Azure Portal)
2. Get the subscription key
3. Add to `frontend/.env`

## Database Schema

### Clients Table
- id, name, country, business_type, organization_size
- created_at, updated_at, created_by

### Sites Table
- id, client_id (FK), name, site_type
- geolocation_polygon (GEOGRAPHY - stores polygons)
- created_at, updated_at, created_by

## API Endpoints

### Clients
- `POST /api/clients` - Create client
- `GET /api/clients` - List/search clients
- `GET /api/clients/{id}` - Get client
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

### Sites
- `POST /api/sites/clients/{client_id}/sites` - Create site
- `GET /api/sites/clients/{client_id}/sites` - List sites
- `GET /api/sites/{id}` - Get site
- `PUT /api/sites/{id}` - Update site
- `DELETE /api/sites/{id}` - Delete site

## Development

### Backend Development
- Use virtual environment
- Run with `--reload` flag for hot reloading
- Check API docs at `/docs` or `/redoc`
- Database migrations with Alembic (setup required)

### Frontend Development
- React hot reloading enabled by default
- Material-UI components for consistent styling
- Azure Maps SDK for polygon drawing
- MSAL for Azure AD authentication

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## Deployment

### Backend
- Deploy to Azure App Service, Azure Container Apps, or similar
- Set environment variables in deployment platform
- Ensure ODBC drivers available in container/VM
- Configure CORS for production frontend URL

### Frontend
- Build: `npm run build`
- Deploy build folder to Azure Static Web Apps, Netlify, or similar
- Update environment variables for production
- Configure backend API URL

## Security Considerations

- Never commit `.env` files
- Rotate Azure AD client secrets regularly
- Use HTTPS in production
- Implement rate limiting (backend)
- Validate all user inputs
- Review CORS settings for production

## Troubleshooting

### Backend Issues
- Check database connection string
- Verify ODBC driver installation
- Check Azure AD credentials
- Review FastAPI logs

### Frontend Issues
- Verify backend API is running
- Check CORS configuration
- Verify Azure AD redirect URI
- Check browser console for errors
- Ensure Azure Maps key is valid

## License

Private - All Rights Reserved

## Support

For issues or questions, contact your development team.
