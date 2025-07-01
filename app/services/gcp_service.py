from google.cloud import storage
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

import logging
from typing import BinaryIO, Optional, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class GCPService:
    def __init__(self):
        self.storage_client = None
        self.bucket = None
        self.initialize_storage_client()
    
    def initialize_storage_client(self):
        """Initialize GCP Storage client with credentials from settings"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GCP_BUCKET_NAME:
                # Only try to initialize if both credentials and bucket are provided
                import os
                if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                    self.storage_client = storage.Client()
                    self.bucket = self.storage_client.bucket(settings.GCP_BUCKET_NAME)
                    logger.info("GCP Storage client initialized successfully")
                else:
                    logger.warning(f"GCP credentials file not found at: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            else:
                logger.info("GCP credentials not configured, Storage client will not be initialized")
        except Exception as e:
            logger.warning(f"GCP Storage client initialization failed: {e}. Application will continue without GCP storage.")
            self.storage_client = None
            self.bucket = None
    
    async def upload_file(self, file_obj: BinaryIO, object_name: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        if not self.storage_client or not self.bucket:
            raise HTTPException(status_code=503, detail="GCP Storage service not available. Please configure GCP credentials.")

        return await run_in_threadpool(self._upload_file_sync, file_obj, object_name, content_type)
    
    def _upload_file_sync(self, file_obj: BinaryIO, object_name: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not self.bucket:
                raise HTTPException(status_code=500, detail="GCP Storage bucket not initialized")
            blob = self.bucket.blob(object_name)

            if content_type:
                blob.content_type = content_type

            blob.upload_from_file(file_obj)
            blob.make_public()

            return {
                "blob_name": blob.name,
                "public_url": blob.public_url
            }

        except Exception as e:
            logger.error(f"Error uploading file to GCP Storage: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
    async def generate_signed_url(self, object_name: str, expiration: int = 3600) -> str:
        if not self.storage_client or not self.bucket:
            raise HTTPException(status_code=500, detail="GCP Storage client not initialized")

        return await run_in_threadpool(self._generate_signed_url_sync, object_name, expiration)

    def _generate_signed_url_sync(self, object_name: str, expiration: int) -> str:
        try:
            if not self.bucket:
                raise HTTPException(status_code=500, detail="GCP Storage bucket not initialized")
            blob = self.bucket.blob(object_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            return url

        except Exception as e:
            logger.error(f"❌ Error generating signed URL: {e}")
            raise HTTPException(status_code=500, detail=str(e))

  
gcp_service = GCPService()