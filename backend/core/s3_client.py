import os
import shutil
from typing import Optional
from backend.config.settings import settings
import boto3

# Initialize S3 client only if provider is s3
s3_client = None
if settings.STORAGE_PROVIDER == "s3":
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


class S3Service:
    """Service for storage operations (S3 or Local)."""

    def __init__(self, client, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name
        self.is_local = settings.STORAGE_PROVIDER == "local"

        if self.is_local:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async def upload_file(
        self, file_path: str, s3_key: str, content_type: Optional[str] = None
    ) -> str:
        """Upload a file to storage."""
        if self.is_local:
            dest_path = os.path.join(settings.UPLOAD_DIR, s3_key)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(file_path, dest_path)
            return dest_path

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.client.upload_file(
            file_path, self.bucket_name, s3_key, ExtraArgs=extra_args
        )

        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

    async def download_file(self, s3_key: str, file_path: str) -> None:
        """Download a file from storage."""
        if self.is_local:
            src_path = os.path.join(settings.UPLOAD_DIR, s3_key)
            shutil.copy2(src_path, file_path)
            return

        self.client.download_file(self.bucket_name, s3_key, file_path)

    async def delete_file(self, s3_key: str) -> None:
        """Delete a file from storage."""
        if self.is_local:
            path = os.path.join(settings.UPLOAD_DIR, s3_key)
            if os.path.exists(path):
                os.remove(path)
            return

        self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a URL for temporary access."""
        if self.is_local:
            return os.path.join(settings.UPLOAD_DIR, s3_key)

        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expiration,
        )

    async def file_exists(self, s3_key: str) -> bool:
        """Check if file exists in storage."""
        if self.is_local:
            return os.path.exists(os.path.join(settings.UPLOAD_DIR, s3_key))

        try:
            self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception:
            return False


s3_service = S3Service(s3_client, settings.AWS_S3_BUCKET)
