# Client Onboarding API - Backend

FastAPI backend for the Client Onboarding application with Azure SQL Database and Azure AD authentication.

## Features

- **Client Management**: CRUD operations for clients with search/filter capabilities
- **Site Management**: CRUD operations for sites with geolocation polygon support
- **Azure AD Authentication**: Secure authentication using Microsoft Azure AD
- **GeoJSON Support**: Store and retrieve geolocation polygons in GeoJSON format
- **Azure SQL Database**: Native support for GEOGRAPHY data types

## Tech Stack

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **GeoAlchemy2**: Geographic extensions for SQLAlchemy
- **Azure SQL Database**: Cloud database with spatial data support
- **Azure AD**: Enterprise authentication
- **Pydantic**: Data validation and settings management

## Prerequisites

- Python 3.11+
- Azure SQL Database instance
- Azure AD tenant and app registration
- ODBC Driver 18 for SQL Server

## Installation

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

4. **Set up database**:
   - Create Azure SQL Database
   - Run migrations (after Alembic setup):
     ```bash
     alembic upgrade head
     ```

## Configuration

Edit `.env` file with your Azure credentials:

```env
# Database
DB_SERVER=your-server.database.windows.net
DB_NAME=client_onboarding
DB_USER=your-username
DB_PASSWORD=your-password

# Azure AD
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-client-id
AZURE_AD_CLIENT_SECRET=your-client-secret

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

## Running the Application

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Clients

- `POST /api/clients` - Create a new client
- `GET /api/clients` - List clients (with search/filter)
- `GET /api/clients/{id}` - Get client by ID
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

### Sites

- `POST /api/sites/clients/{client_id}/sites` - Create site for client
- `GET /api/sites/clients/{client_id}/sites` - List sites for client
- `GET /api/sites/{id}` - Get site by ID
- `PUT /api/sites/{id}` - Update site
- `DELETE /api/sites/{id}` - Delete site

## Database Schema

### Clients Table
- `id`: Primary key
- `name`: Client name
- `country`: Country
- `business_type`: Type of business
- `organization_size`: Organization size
- `created_at`, `updated_at`, `created_by`

### Sites Table
- `id`: Primary key
- `client_id`: Foreign key to clients
- `name`: Site name
- `site_type`: Type of site
- `geolocation_polygon`: GEOGRAPHY (polygon) - stores GeoJSON polygons
- `created_at`, `updated_at`, `created_by`

## GeoJSON Format

Sites accept geolocation polygons in GeoJSON format:

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

## Development Notes

- Database migrations managed with Alembic
- Azure AD tokens validated using JOSE
- CORS configured for frontend communication
- All endpoints support JSON request/response
- Spatial data stored using native Azure SQL GEOGRAPHY type

## License

Private - All Rights Reserved
