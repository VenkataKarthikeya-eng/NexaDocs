import os
from typing import Tuple
from fastapi import HTTPException, status
from app.core.config import settings

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB Limit

class StorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.storage_type = getattr(settings, "STORAGE_TYPE", "LOCAL").upper()
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, doc_id: str, filename: str, content: bytes) -> Tuple[str, str]:
        """
        Validates and saves uploaded PDF document.
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

        safe_filename = f"{doc_id}_{filename}"

        if self.storage_type == "S3" and os.getenv("AWS_S3_BUCKET"):
            bucket = os.getenv("AWS_S3_BUCKET")
            region = os.getenv("AWS_REGION", "us-east-1")
            file_url = f"https://{bucket}.s3.{region}.amazonaws.com/documents/{safe_filename}"
            try:
                import boto3
                s3_client = boto3.client('s3')
                s3_client.put_object(
                    Bucket=bucket,
                    Key=f"documents/{safe_filename}",
                    Body=content,
                    ContentType="application/pdf"
                )
                return f"s3://{bucket}/documents/{safe_filename}", file_url
            except Exception as e:
                print(f"[StorageService] S3 storage warning, falling back to local disk: {e}")

        # Local filesystem storage
        local_path = os.path.join(self.upload_dir, safe_filename)
        with open(local_path, "wb") as f:
            f.write(content)

        file_url = f"/api/v1/documents/{doc_id}/file"
        return local_path, file_url

    def delete_file(self, file_path: str):
        if not file_path:
            return
        if file_path.startswith("s3://") and os.getenv("AWS_S3_BUCKET"):
            try:
                import boto3
                bucket = os.getenv("AWS_S3_BUCKET")
                key = file_path.replace(f"s3://{bucket}/", "")
                s3_client = boto3.client('s3')
                s3_client.delete_object(Bucket=bucket, Key=key)
            except Exception as e:
                print(f"[StorageService] S3 delete error: {e}")
        elif os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"[StorageService] Local file delete error: {e}")

storage_service = StorageService()
