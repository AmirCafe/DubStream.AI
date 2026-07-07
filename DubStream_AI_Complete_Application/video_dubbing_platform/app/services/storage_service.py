"""
Storage Service - Multi-backend file storage
Supports local, AWS S3, and Cloudflare R2 storage
"""

import logging
import os
import shutil
from typing import Optional, Dict
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class StorageService:
    """Handles file storage across multiple backends"""
    
    def __init__(self, backend: str = "local", **kwargs):
        """
        Initialize Storage Service
        
        Args:
            backend: 'local', 's3', or 'r2'
            **kwargs: Backend-specific credentials
        """
        self.backend = backend
        self.s3_client = None
        self.bucket = None
        self.local_path = None
        
        if backend == "s3":
            self._init_s3(**kwargs)
        elif backend == "r2":
            self._init_r2(**kwargs)
        elif backend == "local":
            self._init_local(**kwargs)
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        logger.info(f"Storage initialized: {backend}")
    
    def _init_local(self, path: str = "/data/videos", **kwargs):
        """Initialize local file storage"""
        self.local_path = path
        os.makedirs(self.local_path, exist_ok=True)
        logger.info(f"Local storage path: {self.local_path}")
    
    def _init_s3(self, bucket: str, region: str = "us-east-1",
                 access_key: str = "", secret_key: str = "", **kwargs):
        """Initialize AWS S3 storage"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            self.bucket = bucket
            
            # Test connection
            self.s3_client.head_bucket(Bucket=bucket)
            logger.info(f"S3 storage initialized: {bucket} (region: {region})")
        except ClientError as e:
            logger.error(f"S3 initialization failed: {e}")
            raise
    
    def _init_r2(self, bucket: str, account_id: str,
                 access_key: str = "", secret_key: str = "", **kwargs):
        """Initialize Cloudflare R2 storage"""
        try:
            endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                region_name='auto',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            self.bucket = bucket
            
            # Test connection
            self.s3_client.head_bucket(Bucket=bucket)
            logger.info(f"R2 storage initialized: {bucket}")
        except ClientError as e:
            logger.error(f"R2 initialization failed: {e}")
            raise
    
    def upload_file(self, local_path: str, remote_key: str) -> Dict:
        """
        Upload file to storage backend
        
        Args:
            local_path: Path to local file
            remote_key: Remote file path/key
        
        Returns:
            {
                'success': bool,
                'url': file_url,
                'size': file_size_bytes,
                'backend': backend_name
            }
        """
        if not os.path.exists(local_path):
            logger.error(f"File not found: {local_path}")
            return {'success': False, 'error': 'File not found'}
        
        file_size = os.path.getsize(local_path)
        logger.info(f"Uploading: {local_path} → {remote_key} ({file_size} bytes)")
        
        try:
            if self.backend == "local":
                return self._upload_local(local_path, remote_key, file_size)
            elif self.backend in ["s3", "r2"]:
                return self._upload_cloud(local_path, remote_key, file_size)
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _upload_local(self, local_path: str, remote_key: str, file_size: int) -> Dict:
        """Upload to local storage"""
        try:
            dest_path = os.path.join(self.local_path, remote_key)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.copy2(local_path, dest_path)
            
            url = f"/media/{remote_key}"
            logger.info(f"Local upload successful: {url}")
            
            return {
                'success': True,
                'url': url,
                'size': file_size,
                'backend': 'local'
            }
        except Exception as e:
            logger.error(f"Local upload failed: {e}")
            raise
    
    def _upload_cloud(self, local_path: str, remote_key: str, file_size: int) -> Dict:
        """Upload to S3 or R2"""
        try:
            with open(local_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=remote_key,
                    Body=f,
                    ContentType=self._get_content_type(remote_key)
                )
            
            # Generate URL
            if self.backend == "s3":
                url = f"https://{self.bucket}.s3.amazonaws.com/{remote_key}"
            else:  # R2
                url = f"https://{self.bucket}.r2.cloudflarestorage.com/{remote_key}"
            
            logger.info(f"Cloud upload successful: {remote_key}")
            
            return {
                'success': True,
                'url': url,
                'size': file_size,
                'backend': self.backend
            }
        except Exception as e:
            logger.error(f"Cloud upload failed: {e}")
            raise
    
    def download_file(self, remote_key: str, local_path: str) -> bool:
        """
        Download file from storage backend
        
        Args:
            remote_key: Remote file path/key
            local_path: Local destination path
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Downloading: {remote_key} → {local_path}")
        
        try:
            if self.backend == "local":
                return self._download_local(remote_key, local_path)
            elif self.backend in ["s3", "r2"]:
                return self._download_cloud(remote_key, local_path)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def _download_local(self, remote_key: str, local_path: str) -> bool:
        """Download from local storage"""
        src = os.path.join(self.local_path, remote_key)
        if not os.path.exists(src):
            logger.error(f"File not found: {src}")
            return False
        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        shutil.copy2(src, local_path)
        logger.info(f"Local download successful")
        return True
    
    def _download_cloud(self, remote_key: str, local_path: str) -> bool:
        """Download from S3 or R2"""
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(
                self.bucket,
                remote_key,
                local_path
            )
            
            logger.info(f"Cloud download successful")
            return True
        except Exception as e:
            logger.error(f"Cloud download failed: {e}")
            return False
    
    def delete_file(self, remote_key: str) -> bool:
        """
        Delete file from storage
        
        Args:
            remote_key: Remote file path/key
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting: {remote_key}")
        
        try:
            if self.backend == "local":
                file_path = os.path.join(self.local_path, remote_key)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("File deleted")
                    return True
                return False
            else:
                self.s3_client.delete_object(Bucket=self.bucket, Key=remote_key)
                logger.info("File deleted from cloud")
                return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def file_exists(self, remote_key: str) -> bool:
        """Check if file exists"""
        try:
            if self.backend == "local":
                return os.path.exists(os.path.join(self.local_path, remote_key))
            else:
                self.s3_client.head_object(Bucket=self.bucket, Key=remote_key)
                return True
        except:
            return False
    
    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Get MIME type for file"""
        content_types = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.srt': 'text/plain',
            '.json': 'application/json'
        }
        
        ext = os.path.splitext(filename)[1].lower()
        return content_types.get(ext, 'application/octet-stream')
