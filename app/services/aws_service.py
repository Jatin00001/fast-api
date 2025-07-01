import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional

from app.core.config import settings
import logging

logger = logging.getLogger("services")

class AWSService:
    def __init__(self):
        self.s3_client = None
        self.initialize_s3_client()
    
    def initialize_s3_client(self):
        """Initialize AWS S3 client with credentials from settings"""
        try:
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info("AWS S3 client initialized successfully")
            else:
                logger.warning("AWS credentials not provided, S3 client not initialized")
        except Exception as e:
            logger.error(f"Error initializing AWS S3 client: {e}")
    
    def upload_file(self, file_obj: BinaryIO, object_name: str, content_type: Optional[str] = None) -> dict:
        """
        Upload a file to an S3 bucket
        
        Args:
            file_obj: File object to upload
            object_name: S3 object name
            content_type: Content type of the file
            
        Returns:
            dict: Upload result with status and details
        """
        if not self.s3_client:
            error_msg = "AWS S3 client not initialized"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "SERVICE_NOT_INITIALIZED"
            }

        try:
            logger.info(f"Starting file upload to S3: {object_name}")
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_fileobj(
                file_obj,
                settings.AWS_S3_BUCKET,
                object_name,
                ExtraArgs=extra_args
            )
            
            # Generate URL for the uploaded file
            url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
            
            logger.info(f"Successfully uploaded file to S3: {object_name}")
            
            return {
                "success": True,
                "url": url,
                "object_name": object_name,
                "bucket": settings.AWS_S3_BUCKET
            }
        
        except ClientError as e:
            error_msg = f"AWS ClientError uploading file to S3: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "AWS_CLIENT_ERROR"
            }
        except Exception as e:
            error_msg = f"Unexpected error uploading file to S3: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "UPLOAD_ERROR"
            }
    
    def get_presigned_url(self, object_name: str, expiration: int = 3600) -> dict:
        """
        Generate a presigned URL for an S3 object
        
        Args:
            object_name: S3 object name
            expiration: Time in seconds for the URL to remain valid
            
        Returns:
            dict: Presigned URL result
        """
        if not self.s3_client:
            error_msg = "AWS S3 client not initialized"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "SERVICE_NOT_INITIALIZED"
            }

        try:
            logger.info(f"Generating presigned URL for S3 object: {object_name}")
            
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_S3_BUCKET,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Successfully generated presigned URL for: {object_name}")
            
            return {
                "success": True,
                "presigned_url": response,
                "expiration": expiration,
                "object_name": object_name
            }
        
        except ClientError as e:
            error_msg = f"AWS ClientError generating presigned URL: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "AWS_CLIENT_ERROR"
            }
        except Exception as e:
            error_msg = f"Unexpected error generating presigned URL: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "PRESIGNED_URL_ERROR"
            }

    def delete_file(self, object_name: str) -> dict:
        """
        Delete a file from S3 bucket
        
        Args:
            object_name: S3 object name
            
        Returns:
            dict: Deletion result
        """
        if not self.s3_client:
            error_msg = "AWS S3 client not initialized"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "SERVICE_NOT_INITIALIZED"
            }

        try:
            logger.info(f"Deleting file from S3: {object_name}")
            
            self.s3_client.delete_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=object_name
            )
            
            logger.info(f"Successfully deleted file from S3: {object_name}")
            
            return {
                "success": True,
                "object_name": object_name,
                "message": "File deleted successfully"
            }
            
        except ClientError as e:
            error_msg = f"AWS ClientError deleting file from S3: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "AWS_CLIENT_ERROR"
            }
        except Exception as e:
            error_msg = f"Unexpected error deleting file from S3: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "DELETE_ERROR"
            }

    def list_files(self, prefix: str = "") -> dict:
        """
        List files in S3 bucket
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            dict: List of files result
        """
        if not self.s3_client:
            error_msg = "AWS S3 client not initialized"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "SERVICE_NOT_INITIALIZED"
            }

        try:
            logger.info(f"Listing files from S3 with prefix: {prefix}")
            
            response = self.s3_client.list_objects_v2(
                Bucket=settings.AWS_S3_BUCKET,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [
                    {
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'],
                        "etag": obj['ETag']
                    }
                    for obj in response['Contents']
                ]
            
            logger.info(f"Successfully listed {len(files)} files from S3")
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "prefix": prefix
            }
            
        except ClientError as e:
            error_msg = f"AWS ClientError listing files from S3: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "AWS_CLIENT_ERROR"
            }
        except Exception as e:
            error_msg = f"Unexpected error listing files from S3: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_code": "LIST_ERROR"
            }

# Create a global instance
aws_service = AWSService()