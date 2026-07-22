# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack client onboarding application with geolocation support:
- **Frontend**: React 18 + Material-UI + Azure Maps (port 3000)
- **Backend**: FastAPI (Python) - all API endpoints (port 8000)
- **Database**: Azure SQL Database with GEOGRAPHY spatial data support
- **Authentication**: Azure AD (Entra ID) via MSAL

**Important**: Node.js is ONLY for React development tools. All backend APIs are Python/FastAPI, not Node.js.

## Development Commands

### Backend (FastAPI)

```bash
cd backend

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server (with hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
pytest

# Database operations (if Alembic is configured)
alembic upgrade head
alembic revision --autogenerate -m "description"
```

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend (React)

```bash
cd frontend

# Setup
npm install

# Run development server (with hot reload)
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Architecture

### Backend Structure

```
backend/app/
├── main.py              # FastAPI app entry point, CORS, router registration
├── config.py            # Settings from environment variables (pydantic-settings)
├── database.py          # SQLAlchemy engine, session, Base, get_db() dependency
├── models/              # SQLAlchemy ORM models
│   ├── client.py        # Client table with sites relationship
│   └── site.py          # Site table with GEOGRAPHY polygon column
├── schemas/             # Pydantic schemas for request/response validation
│   ├── client.py        # ClientCreate, ClientRead, ClientUpdate, ClientWithSites
│   └── site.py          # SiteCreate, SiteRead, SiteUpdate (handles GeoJSON)
├── routers/             # API endpoint implementations
│   ├── clients.py       # /api/clients endpoints
│   └── sites.py         # /api/sites endpoints
└── auth/
    └── azure_ad.py      # Azure AD JWT validation, get_current_user dependency
```

### Frontend Structure

```
frontend/src/
├── App.jsx              # Main routing, ProtectedRoute wrapper using MSAL
├── index.js             # React entry point, MSAL provider setup
├── theme.js             # Material-UI theme configuration
├── components/
│   ├── clients/         # ClientList, ClientForm components
│   ├── sites/           # SiteList, SiteForm (with Azure Maps integration)
│   └── common/          # Layout, Navigation components
└── services/            # API layer
    ├── api.js           # Axios instance with auth header interceptor
    ├── clientService.js # Client CRUD operations
    └── siteService.js   # Site CRUD operations
```

### Database Models

**Client** (clients table):
- Standard fields: id, name, country, business_type, organization_size
- Timestamps: created_at, updated_at (using SQL Server's getutcdate())
- Auth tracking: created_by
- Relationship: One-to-many with sites (cascade delete)

**Site** (sites table):
- Standard fields: id, client_id (FK), name, site_type
- Geospatial: geolocation_polygon (GEOGRAPHY POLYGON, SRID 4326)
- Timestamps: created_at, updated_at
- Auth tracking: created_by
- Relationship: Many-to-one with client

### Geospatial Data Handling

Sites use **GeoJSON Polygon format** for geolocation data:

```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [-122.4194, 37.7749],
      [-122.4094, 37.7749],
      [-122.4094, 37.7649],
      [-122.4194, 37.7649],
      [-122.4194, 37.7749]
    ]
  ]
}
```

**Backend**: GeoAlchemy2 converts between GeoJSON (API) ↔ WKT (database GEOGRAPHY type)
**Frontend**: Azure Maps Drawing Tools for polygon creation/editing

### Azure SQL Connection

Database connection uses **pymssql** driver (doesn't require ODBC drivers):
- Connection string format: `mssql+pymssql://{user}@{server}:{password}@{host}:1433/{database}`
- Azure SQL requires username in format: `{username}@{servername}`
- Constructed in `backend/app/config.py` via the `database_url` property

### Authentication Flow

**Current state**: Azure AD authentication is implemented but NOT currently enforced on endpoints (see `backend/app/main.py:6` - auth import is commented out).

**Frontend**:
1. MSAL React library handles Azure AD login
2. Protected routes use `ProtectedRoute` wrapper (frontend/src/App.jsx:12)
3. Axios interceptor adds JWT token to all API requests

**Backend**:
4. Azure AD JWT validation in `backend/app/auth/azure_ad.py`
5. `get_current_user()` dependency verifies token using Azure AD signing keys
6. To enforce auth, import and use `Depends(get_current_user)` in router endpoints

### API Endpoints

**Clients** (`/api/clients`):
- POST `/` - Create client
- GET `/` - List clients with search/filter (query params: skip, limit, search, country, business_type)
- GET `/{client_id}` - Get client with sites (uses ClientWithSites schema)
- PUT `/{client_id}` - Update client
- DELETE `/{client_id}` - Delete client (cascades to sites)

**Sites** (`/api/sites`):
- POST `/clients/{client_id}/sites` - Create site for client
- GET `/clients/{client_id}/sites` - List sites for client
- GET `/{site_id}` - Get site by ID
- PUT `/{site_id}` - Update site
- DELETE `/{site_id}` - Delete site

### Configuration

Both frontend and backend require `.env` files (copy from `.env.example`):

**Backend** (`backend/.env`):
- Database: DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD
- Azure AD: AZURE_AD_TENANT_ID, AZURE_AD_CLIENT_ID, AZURE_AD_CLIENT_SECRET
- API: API_HOST, API_PORT, CORS_ORIGINS

**Frontend** (`frontend/.env`):
- API: REACT_APP_API_URL (backend URL)
- Azure AD: REACT_APP_AZURE_AD_CLIENT_ID, REACT_APP_AZURE_AD_TENANT_ID, REACT_APP_AZURE_AD_REDIRECT_URI
- Azure Maps: REACT_APP_AZURE_MAPS_KEY

## Development Notes

### Database Queries with MS SQL Server

**CRITICAL**: MS SQL Server requires `ORDER BY` when using `OFFSET/LIMIT` (see `backend/app/routers/clients.py:62`). Always include `.order_by()` before `.offset().limit()`.

### SQLAlchemy with Azure SQL

- Use `func.getutcdate()` for SQL Server timestamps (not `func.now()`)
- GEOGRAPHY columns work with GeoAlchemy2's `Geography('POLYGON', srid=4326)`
- Connection requires `pool_pre_ping=True` for reliability with cloud databases

### Frontend Routing

All routes are protected by Azure AD authentication:
- `/clients` - Client list
- `/clients/new` - Create client
- `/clients/:id` - Edit client
- `/clients/:clientId/sites` - Site list for client
- `/clients/:clientId/sites/new` - Create site
- `/sites/:id` - Edit site

Root path `/` redirects to `/clients`.

### CORS Configuration

Backend CORS settings in `backend/app/config.py`:
- Default: `http://localhost:3000`
- Supports multiple origins (comma-separated)
- Must be configured for production frontend URL

### Material-UI Integration

Frontend uses Material-UI v5 with:
- Custom theme in `frontend/src/theme.js`
- MUI Data Grid for client/site tables
- MUI icons from `@mui/icons-material`
- Emotion for styled components

### Azure Maps Integration

Frontend uses Azure Maps Control and Drawing Tools:
- Initialize with `REACT_APP_AZURE_MAPS_KEY`
- Drawing manager for polygon creation
- GeoJSON format for data exchange
- SRID 4326 (WGS84) coordinate system
