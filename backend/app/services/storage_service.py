import os
import re
from typing import Tuple, Optional
from fastapi import HTTPException, status
from app.core.config import settings

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB Limit


class StorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.storage_type = getattr(settings, "STORAGE_TYPE", "LOCAL").upper()
        self.bucket_name = getattr(settings, "S3_BUCKET_NAME", "nexadocs-files")
        self.endpoint_url = getattr(settings, "S3_ENDPOINT_URL", "")
        self.region = getattr(settings, "S3_REGION", "us-east-2")
        self.access_key = getattr(settings, "S3_ACCESS_KEY_ID", "")
        self.secret_key = getattr(settings, "S3_SECRET_ACCESS_KEY", "")
        self.presigned_expiration = getattr(settings, "S3_PRESIGNED_EXPIRATION_SECONDS", 3600)
        self._s3_client = None

        os.makedirs(self.upload_dir, exist_ok=True)

    def _get_s3_client(self):
        """Lazy-initializes S3 client with configurable S3-compatible endpoint (e.g. Neon Object Storage)."""
        if self._s3_client is not None:
            return self._s3_client

        try:
            import boto3
            from botocore.config import Config

            boto_config = Config(
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'standard'}
            )

            client_kwargs = {
                "service_name": "s3",
                "config": boto_config
            }

            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url
            if self.region:
                client_kwargs["region_name"] = self.region
            if self.access_key and self.secret_key:
                client_kwargs["aws_access_key_id"] = self.access_key
                client_kwargs["aws_secret_access_key"] = self.secret_key

            self._s3_client = boto3.client(**client_kwargs)
            return self._s3_client
        except Exception as e:
            print(f"[StorageService] Failed to initialize S3 client: {e}")
            return None

    def _parse_s3_uri(self, uri: str) -> Tuple[str, str]:
        """Parses s3://bucket/key into (bucket, key)."""
        clean = uri.replace("s3://", "")
        parts = clean.split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key

    async def save_file(self, doc_id: str, filename: str, content: bytes) -> Tuple[str, str]:
        """
        Validates and saves uploaded PDF document to S3 or local disk.
        Enforces 25MB maximum size limit, PDF extension, and PDF header magic bytes.
        Returns tuple of (file_path, file_url).
        """
        if not content or len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size limit of 25MB (File size: {round(len(content)/(1024*1024), 2)}MB)."
            )

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Only PDF documents are allowed."
            )

        # Validate PDF magic header bytes
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file content: Missing standard PDF magic header (%PDF-)."
            )

        # Sanitize filename
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        safe_filename = f"{doc_id}_{clean_name}"

        # S3-compatible storage (Neon Object Storage / S3)
        if self.storage_type == "S3":
            s3 = self._get_s3_client()
            if s3 is not None and self.bucket_name:
                key = f"documents/{safe_filename}"
                try:
                    s3.put_object(
                        Bucket=self.bucket_name,
                        Key=key,
                        Body=content,
                        ContentType="application/pdf"
                    )
                    s3_uri = f"s3://{self.bucket_name}/{key}"
                    file_url = f"/api/v1/documents/{doc_id}/file"
                    return s3_uri, file_url
                except Exception as e:
                    print(f"[StorageService] S3 put_object error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to store file in object storage: {str(e)}"
                    )

        # Local filesystem storage fallback
        local_path = os.path.join(self.upload_dir, safe_filename)
        with open(local_path, "wb") as f:
            f.write(content)

        file_url = f"/api/v1/documents/{doc_id}/file"
        return local_path, file_url

    def get_file_bytes(self, file_path: str) -> bytes:
        """Retrieves raw file bytes from S3 or local filesystem."""
        if not file_path:
            raise ValueError("File path cannot be empty.")

        if file_path.startswith("s3://"):
            s3 = self._get_s3_client()
            if not s3:
                raise RuntimeError("S3 client is not available.")
            bucket, key = self._parse_s3_uri(file_path)
            try:
                response = s3.get_object(Bucket=bucket, Key=key)
                return response['Body'].read()
            except Exception as e:
                print(f"[StorageService] S3 get_object error for {file_path}: {e}")
                raise FileNotFoundError(f"File not found in object storage: {e}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found at path: {file_path}")

        with open(file_path, "rb") as f:
            return f.read()

    def generate_presigned_download_url(
        self,
        file_path: str,
        filename: Optional[str] = None,
        expiration: Optional[int] = None
    ) -> Optional[str]:
        """
        Generates a short-lived presigned download URL for private S3-compatible objects.
        Returns None for local files.
        """
        if not file_path or not file_path.startswith("s3://"):
            return None

        s3 = self._get_s3_client()
        if not s3:
            return None

        bucket, key = self._parse_s3_uri(file_path)
        params = {"Bucket": bucket, "Key": key}
        if filename:
            params["ResponseContentDisposition"] = f'inline; filename="{filename}"'

        try:
            exp = expiration or self.presigned_expiration
            url = s3.generate_presigned_url("get_object", Params=params, ExpiresIn=exp)
            return url
        except Exception as e:
            print(f"[StorageService] Failed to generate presigned URL: {e}")
            return None

    def file_exists(self, file_path: str) -> bool:
        """Verifies if a file exists either in S3 or on local filesystem."""
        if not file_path:
            return False

        if file_path.startswith("s3://"):
            s3 = self._get_s3_client()
            if not s3:
                return False
            bucket, key = self._parse_s3_uri(file_path)
            try:
                s3.head_object(Bucket=bucket, Key=key)
                return True
            except Exception:
                return False

        return os.path.exists(file_path)

    def delete_file(self, file_path: str) -> bool:
        """Safely removes file from S3 or local filesystem."""
        if not file_path:
            return False

        if file_path.startswith("s3://"):
            s3 = self._get_s3_client()
            if not s3:
                return False
            bucket, key = self._parse_s3_uri(file_path)
            try:
                s3.delete_object(Bucket=bucket, Key=key)
                return True
            except Exception as e:
                print(f"[StorageService] S3 delete error for {file_path}: {e}")
                return False

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"[StorageService] Local file delete error: {e}")
                return False

        return False


storage_service = StorageService()
