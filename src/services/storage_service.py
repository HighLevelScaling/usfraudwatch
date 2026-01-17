import os
import uuid
from datetime import datetime
from typing import Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError

from src.utils.config import get_settings
from src.utils.security import sanitize_filename

settings = get_settings()


class StorageService:
    """Service for file storage (local or S3)."""

    def __init__(self):
        self.storage_type = settings.storage_type
        self.upload_dir = settings.upload_dir
        self.s3_bucket = settings.s3_bucket

        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
            )

    def _generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = sanitize_filename(original_filename)
        return f"{timestamp}_{unique_id}_{safe_filename}"

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = "documents",
    ) -> dict:
        """
        Upload a file to storage.
        
        Returns dict with:
        - file_path: Local path (if local storage)
        - s3_key: S3 key (if S3 storage)
        - url: Public URL to access the file
        """
        unique_filename = self._generate_filename(filename)
        
        if self.storage_type == "s3":
            return await self._upload_to_s3(file, unique_filename, content_type, folder)
        else:
            return await self._upload_to_local(file, unique_filename, folder)

    async def _upload_to_local(
        self,
        file: BinaryIO,
        filename: str,
        folder: str,
    ) -> dict:
        """Upload file to local filesystem."""
        folder_path = os.path.join(self.upload_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, filename)
        
        # Write file
        content = file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return relative path for storage
        relative_path = os.path.join(folder, filename)
        
        return {
            "file_path": relative_path,
            "s3_key": None,
            "url": f"/uploads/{relative_path}",
            "file_size": len(content),
        }

    async def _upload_to_s3(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str,
    ) -> dict:
        """Upload file to S3."""
        s3_key = f"{folder}/{filename}"
        content = file.read()
        
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=content,
                ContentType=content_type,
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to upload to S3: {e}")
        
        # Generate URL
        url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
        
        return {
            "file_path": None,
            "s3_key": s3_key,
            "url": url,
            "file_size": len(content),
        }

    async def delete_file(
        self,
        file_path: Optional[str] = None,
        s3_key: Optional[str] = None,
    ) -> bool:
        """Delete a file from storage."""
        if self.storage_type == "s3" and s3_key:
            try:
                self.s3_client.delete_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                )
                return True
            except ClientError:
                return False
        
        elif file_path:
            full_path = os.path.join(self.upload_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        
        return False

    def get_download_url(
        self,
        file_path: Optional[str] = None,
        s3_key: Optional[str] = None,
        expires_in: int = 3600,
    ) -> Optional[str]:
        """Get a download URL for a file."""
        if self.storage_type == "s3" and s3_key:
            try:
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.s3_bucket, "Key": s3_key},
                    ExpiresIn=expires_in,
                )
                return url
            except ClientError:
                return None
        
        elif file_path:
            return f"/uploads/{file_path}"
        
        return None


storage_service = StorageService()
