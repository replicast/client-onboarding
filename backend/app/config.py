"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database settings
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"

    # Azure AD settings
    AZURE_AD_TENANT_ID: str
    AZURE_AD_CLIENT_ID: str
    AZURE_AD_CLIENT_SECRET: str

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    # Azure Blob Storage settings
    AZURE_STORAGE_ACCOUNT_NAME: str = ""
    AZURE_STORAGE_ACCOUNT_KEY: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "client-documents"

    @property
    def database_url(self) -> str:
        """Construct Azure SQL connection string using pymssql (doesn't require ODBC drivers)"""
        # For Azure SQL, use username@servername format
        server_name = self.DB_SERVER.split('.')[0]
        azure_user = f"{self.DB_USER}@{server_name}"
        return (
            f"mssql+pymssql://{azure_user}:{self.DB_PASSWORD}"
            f"@{self.DB_SERVER}:1433/{self.DB_NAME}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
