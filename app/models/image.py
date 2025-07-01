from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from typing import Optional
from fastapi import HTTPException

from app.db.sql import Base
from app.models.file import File

class Image(Base):
    """
    Image model for storing image metadata and relationships
    """
    __tablename__ = "images"

    # Primary key and timestamps
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Image URLs and file relationships
    image_url = Column(String)
    backup_image_of_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    filename = Column(String)
    premier_image_url = Column(String)
    backup_image_url = Column(String)

    # Metadata and organization
    order = Column(Integer)
    description = Column(Text)
    
    # Status tracking
    is_deleted = Column(Boolean, default=False)
    is_updated = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional metadata
    image_score = Column(JSON, nullable=True)


    @classmethod
    def build(
        cls,
        filename: str,
        image_url: str,
        backup_image_url: Optional[str] = None,
        description: Optional[str] = None,
        order: int = 0,
        file_id: Optional[int] = None,
        premier_image_url: Optional[str] = None,
        **kwargs
    ) -> "Image":
        # Normalize filename
        if filename:
            filename = filename.lower().strip()
            import re
            filename = re.sub(r'\s+', '-', filename)
        
        # Set premier_image_url if not provided
        if not premier_image_url:
            premier_image_url = cls.replace_image_from_string(image_url)
        
        return cls(
            filename=filename,
            image_url=image_url,
            backup_image_url=backup_image_url,
            premier_image_url=premier_image_url,
            description=description,
            order=order,
            file_id=file_id,
            **kwargs
        )
       
    @classmethod
    async def build_from_file(cls, file: Optional[File] = None, **kwargs) -> "Image":
        
        if file:
            try:
                # If file has a blob_name, try to get the blob
                if hasattr(file, 'blob_name') and file.blob_name:
                    blob = File.get_blob(file.blob_name)
                    public_url = blob.public_url if blob else file.public_url
                else:
                    public_url = file.public_url
                
                # Try to process with ImageKit-style URL if available
                imagekit_url = cls.replace_image_from_string(public_url) if public_url else None
                
                # Update kwargs with file information
                kwargs.update({
                    "file_id": file.id,
                    "backup_image_url": public_url if imagekit_url else None,
                    "image_url": imagekit_url or public_url
                })

                # Set filename if not provided
                if not kwargs.get("filename") and hasattr(file, 'filename'):
                    kwargs["filename"] = file.filename
                    
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to process image from file: {str(e)}"
                )

        return cls(**kwargs)

    @classmethod
    def build_from_url(
        cls,
        image_url: str,
        filename: Optional[str] = None,
        description: Optional[str] = None,
        order: int = 0,
    ) -> "Image":
        if not filename:
            # Extract filename from URL
            filename = image_url.split('/')[-1] if image_url else "unknown"
        
        return cls.build(
            filename=filename,
            image_url=image_url,
            description=description,
            order=order
        )

    

    @staticmethod
    def replace_image_from_string(url: str) -> Optional[str]:
        """
        Replace or convert URL to ImageKit-style URL if needed.
        This is a utility function for URL transformation.
        
        Args:
            url: Original image URL
            
        Returns:
            Transformed URL or original URL if no transformation needed
        """
        if not url:
            return None
            
        # Define URL patterns that should be replaced
        existing_urls = [
            "https://storage.googleapis.com/staging-luxe.appspot.com",
            "https://storage.googleapis.com/preproduction-ratedapartments.appspot.com",
            "https://storage.googleapis.com",
            "https://lh3.googleusercontent.com",
            "http://lh3.googleusercontent.com",
        ]

        # ImageKit host URL (customize as needed)
        imagekit_host_url = "https://example.com/images"

        # Replace known URL patterns
        for prefix in existing_urls:
            if url.startswith(prefix):
                return url.replace(prefix, imagekit_host_url)

        # Return original URL if no transformation is needed
        return url  