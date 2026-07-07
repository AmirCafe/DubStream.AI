import boto3
from app.core.config import settings
import os

class StorageService:
    def __init__(self):
        if settings.STORAGE_BACKEND == "s3":
            self.s3 = boto3.client(
                "s3",
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            )
            self.bucket = settings.S3_BUCKET
        elif settings.STORAGE_BACKEND == "r2":
            self.s3 = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                region_name="auto",
                aws_access_key_id=settings.R2_ACCESS_KEY,
                aws_secret_access_key=settings.R2_SECRET_KEY,
            )
            self.bucket = settings.R2_BUCKET
        else:
            os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    
    async def upload_file(self, file_path: str, key: str) -> str:
        if settings.STORAGE_BACKEND == "local":
            dest = os.path.join(settings.LOCAL_STORAGE_PATH, key)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(file_path, "rb") as f:
                with open(dest, "wb") as d:
                    d.write(f.read())
            return f"{settings.API_BASE_URL}/media/{key}"
        else:
            with open(file_path, "rb") as f:
                self.s3.upload_fileobj(f, self.bucket, key)
            
            if settings.CLOUDFLARE_CDN_URL:
                return f"{settings.CLOUDFLARE_CDN_URL}/{key}"
            return f"https://{self.bucket}.s3.amazonaws.com/{key}"
    
    async def delete_file(self, key: str):
        if settings.STORAGE_BACKEND != "local":
            self.s3.delete_object(Bucket=self.bucket, Key=key)
