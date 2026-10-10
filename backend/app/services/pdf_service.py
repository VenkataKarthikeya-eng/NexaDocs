import os
import io
from typing import List, Dict, Any, Optional

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

import pypdf


class PDFService:
    @staticmethod
    def extract_text_and_pages_from_bytes(content: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Extracts verified text content and exact physical page metadata directly from PDF bytes in memory.
        Uses PyMuPDF (fitz) as primary high-performance engine with PyPDF as fallback.
        Raises ValueError with clear message for corrupt, empty, scanned, or encrypted PDFs.
        """
        if not content or len(content) == 0:
            raise ValueError("Uploaded PDF file is completely empty (0 bytes).")

        # Validate PDF magic header bytes
        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid file format: File header does not match PDF specification (%PDF-).")

        pages = []
        full_text = ""
        total_pages = 0
        has_images = False

        # 1. Primary Engine: PyMuPDF (fitz) from byte stream
        mupdf_success = False
        if fitz is not None:
            try:
                doc = fitz.open(stream=content, filetype="pdf")
                if doc.is_encrypted:
                    doc.close()
                    raise ValueError("Password-protected or encrypted PDF documents are not supported. Please remove the password and try again.")

                total_pages = doc.page_count
                if total_pages == 0:
                    doc.close()
                    raise ValueError("PDF document contains 0 pages.")

                for idx, page in enumerate(doc):
                    page_num = idx + 1
                    page_text = page.get_text("text") or ""
                    clean_page_text = page_text.strip()
                    pages.append({
                        "page_number": page_num,
                        "text": clean_page_text
                    })
                    if clean_page_text:
                        full_text += f"\n--- Page {page_num} ---\n" + clean_page_text

                    if not has_images:
                        image_list = page.get_images()
                        if image_list:
                            has_images = True

                doc.close()
                mupdf_success = True
            except ValueError:
                raise
            except Exception as e:
                # If PyMuPDF fails on non-standard formatting, fall back to PyPDF
                pages.clear()
                full_text = ""
                mupdf_success = False

        # 2. Fallback Engine: PyPDF from BytesIO stream
        if not mupdf_success:
            try:
                pdf_stream = io.BytesIO(content)
                reader = pypdf.PdfReader(pdf_stream)
                if reader.is_encrypted:
                    raise ValueError("Password-protected or encrypted PDF documents are not supported. Please remove the password and try again.")

                total_pages = len(reader.pages)
                if total_pages == 0:
                    raise ValueError("PDF document contains 0 pages.")

                for idx, page in enumerate(reader.pages):
                    page_num = idx + 1
                    try:
                        page_text = page.extract_text() or ""
                    except Exception:
                        page_text = ""
                    clean_page_text = page_text.strip()
                    pages.append({
                        "page_number": page_num,
                        "text": clean_page_text
                    })
                    if clean_page_text:
                        full_text += f"\n--- Page {page_num} ---\n" + clean_page_text
                    if not has_images and len(page.images) > 0:
                        has_images = True
            except ValueError:
                raise
            except Exception as e:
                raise ValueError(f"Unable to parse PDF document: Corrupted or unreadable format ({str(e)}).")

        # Verify whether searchable text was extracted
        total_text_length = len(full_text.strip())
        if total_text_length < 25:
            if has_images or total_pages > 0:
                raise ValueError("No searchable text found in this PDF. The document appears to be scanned or image-only, which requires an OCR preprocessing layer.")
            else:
                raise ValueError("PDF document contains no readable text content.")

        return {
            "page_count": total_pages,
            "full_text": full_text.strip(),
            "pages": pages
        }

    @classmethod
    def extract_text_and_pages(cls, file_path: str) -> Dict[str, Any]:
        """
        Extracts verified text content and page metadata from a file path or s3:// URI.
        Supports both local paths and S3 object storage references.
        """
        if not file_path:
            raise ValueError("File path cannot be empty.")

        if file_path.startswith("s3://"):
            from app.services.storage_service import storage_service
            content = storage_service.get_file_bytes(file_path)
            return cls.extract_text_and_pages_from_bytes(content, filename=os.path.basename(file_path))

        if not os.path.exists(file_path):
            raise ValueError(f"PDF file not found at path: {file_path}")

        with open(file_path, "rb") as f:
            content = f.read()

        return cls.extract_text_and_pages_from_bytes(content, filename=os.path.basename(file_path))

    @staticmethod
    def chunk_text(pages: List[Dict[str, Any]], chunk_size: int = 700, overlap: int = 150) -> List[Dict[str, Any]]:
        """
        Splits extracted page text into overlapping chunks along natural sentence/paragraph boundaries.
        Strictly preserves exact physical 1-indexed PDF page numbers for every chunk.
        """
        chunks = []
        chunk_id = 0

        for page in pages:
            text = page.get("text", "")
            page_num = page.get("page_number", 1)

            if not text or not text.strip():
                continue

            text_len = len(text)
            start = 0

            while start < text_len:
                target_end = min(start + chunk_size, text_len)
                actual_end = target_end

                # Find natural boundary if not at end of text
                if target_end < text_len:
                    search_window = text[max(start, target_end - 150):target_end]
                    break_pos = -1
                    for sep in ["\n\n", ".\n", ". ", "?\n", "? ", "!\n", "! ", "\n", "; ", " "]:
                        p = search_window.rfind(sep)
                        if p != -1:
                            break_pos = max(start, target_end - 150) + p + len(sep)
                            break
                    if break_pos > start:
                        actual_end = break_pos

                chunk_str = text[start:actual_end].strip()
                if chunk_str and len(chunk_str) >= 20:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "page": page_num,
                        "text": chunk_str,
                        "char_start": start,
                        "char_end": actual_end
                    })
                    chunk_id += 1

                step = actual_end - overlap
                if step <= start:
                    step = actual_end
                start = step

        if not chunks:
            raise ValueError("No valid text chunks could be generated from document pages.")

        return chunks


pdf_service = PDFService()
