"""Azure Blob Storage service for document management"""
import uuid
from datetime import datetime, timedelta
from typing import BinaryIO, Optional
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas, ContentSettings
from ..config import settings


class BlobStorageService:
    """Service for interacting with Azure Blob Storage"""

    def __init__(self):
        self._client: Optional[BlobServiceClient] = None

    @property
    def client(self) -> BlobServiceClient:
        """Lazy initialization of blob service client"""
        if self._client is None:
            if not settings.AZURE_STORAGE_ACCOUNT_NAME or not settings.AZURE_STORAGE_ACCOUNT_KEY:
                raise ValueError("Azure Storage credentials not configured")
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={settings.AZURE_STORAGE_ACCOUNT_NAME};"
                f"AccountKey={settings.AZURE_STORAGE_ACCOUNT_KEY};"
                f"EndpointSuffix=core.windows.net"
            )
            self._client = BlobServiceClient.from_connection_string(connection_string)
        return self._client

    @property
    def container_name(self) -> str:
        return settings.AZURE_STORAGE_CONTAINER_NAME

    def _get_container_client(self):
        """Get container client, creating container if it doesn't exist"""
        container_client = self.client.get_container_client(self.container_name)
        if not container_client.exists():
            container_client.create_container()
        return container_client

    def generate_blob_name(self, client_id: int, original_filename: str) -> str:
        """Generate a unique blob name for the document"""
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = original_filename.replace(" ", "_")
        return f"clients/{client_id}/documents/{unique_id}_{safe_filename}"

    async def upload_document(
        self,
        file: BinaryIO,
        client_id: int,
        original_filename: str,
        content_type: str = "application/pdf"
    ) -> tuple[str, int]:
        """
        Upload a document to blob storage.

        Returns:
            Tuple of (blob_name, file_size)
        """
        blob_name = self.generate_blob_name(client_id, original_filename)
        container_client = self._get_container_client()
        blob_client = container_client.get_blob_client(blob_name)

        # Read file content
        content = file.read()
        file_size = len(content)

        # Upload to blob storage
        blob_client.upload_blob(
            content,
            blob_type="BlockBlob",
            content_settings=ContentSettings(content_type=content_type),
            overwrite=True
        )

        return blob_name, file_size

    def generate_sas_url(self, blob_name: str, expiry_hours: int = 1) -> str:
        """Generate a SAS URL for secure, time-limited access to a blob"""
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=settings.AZURE_STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )

        return (
            f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
            f"{self.container_name}/{blob_name}?{sas_token}"
        )

    async def delete_document(self, blob_name: str) -> bool:
        """Delete a document from blob storage"""
        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            return True
        except Exception:
            return False

    async def delete_client_documents(self, client_id: int) -> int:
        """Delete all documents for a client. Returns count of deleted blobs."""
        prefix = f"clients/{client_id}/documents/"
        container_client = self._get_container_client()
        deleted_count = 0

        for blob in container_client.list_blobs(name_starts_with=prefix):
            blob_client = container_client.get_blob_client(blob.name)
            blob_client.delete_blob()
            deleted_count += 1

        return deleted_count


# Singleton instance
blob_storage_service = BlobStorageService()
