from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.sql import Base
from app.services.gcp_service import gcp_service
from google.cloud import storage
from app.core.config import settings

from fastapi import UploadFile, HTTPException
from app.utility.utils import secure_filename
from uuid import uuid4
from starlette.concurrency import run_in_threadpool

import os
import imghdr

ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "gif"}


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    identifier = Column(String, unique=True, nullable=True)
    filename = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    blob_name = Column(String, nullable=True)
    public_url = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)

    @classmethod
    async def build_by_field_storage_v2(cls, field_storage: UploadFile, supp_id=None, **kwargs):
        return await cls.build_by_file(
            input_file=field_storage.file,
            content_type=field_storage.content_type,
            filename=field_storage.filename,
            supp_id=supp_id,
            **kwargs
        )

    @classmethod
    async def build_by_file(cls, input_file, content_type, filename, supp_id=None, **kwargs):
        # Read first 512 bytes in thread-safe way
        head_bytes = await run_in_threadpool(input_file.read, 512)
        extension = imghdr.what(None, h=head_bytes)

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not allowed")

        # Reset stream before upload
        await run_in_threadpool(input_file.seek, 0)

        # Secure filename
        secure_name = secure_filename(filename)
        unique_filename = f"{uuid4().hex}_{secure_name}"

        # Upload to GCP
        result = await gcp_service.upload_file(
            file_obj=input_file,
            object_name=unique_filename,
            content_type=content_type
        )
        public_url = result.get("public_url")
        blob_name = result.get("blob_name")
        

        # Reset and get file size
        await run_in_threadpool(input_file.seek, 0)
        full_content = await run_in_threadpool(input_file.read)
        size = len(full_content)

        return cls(
            identifier=f"{uuid4().hex}-{os.path.splitext(secure_name)[0]}",
            filename=secure_name,
            content_type=content_type,
            blob_name=blob_name,         # ✅ Now a string
            public_url=public_url,       # ✅ Now a string
            size=size,
            **kwargs
        )
    @classmethod
    def get_blob(cls, blob_name):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(settings.GCP_BUCKET_NAME)
        blob = bucket.get_blob(blob_name)
        return blob