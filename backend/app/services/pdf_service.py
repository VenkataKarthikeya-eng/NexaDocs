import os
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
    def extract_text_and_pages(file_path: str) -> Dict[str, Any]:
        """
        Extracts verified text content and exact physical page metadata from a PDF file.
        Uses PyMuPDF (fitz) as primary high-performance engine with PyPDF as fallback.
        Raises ValueError with clear message for corrupt, empty, scanned, or encrypted PDFs.
        """
        if not os.path.exists(file_path):
            raise ValueError(f"PDF file not found at path: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("Uploaded PDF file is completely empty (0 bytes).")

        # Validate PDF magic header bytes
        with open(file_path, "rb") as f:
            header = f.read(8)
            if not header.startswith(b"%PDF-"):
                raise ValueError("Invalid file format: File header does not match PDF specification (%PDF-).")

        pages = []
        full_text = ""
        total_pages = 0
        has_images = False

        # Attempt extraction via PyMuPDF (fitz)
        mupdf_success = False
        if fitz is not None:
            try:
                doc = fitz.open(file_path)
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

        # Fallback to PyPDF if PyMuPDF not available or encountered parsing error
        if not mupdf_success:
            try:
                reader = pypdf.PdfReader(file_path)
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
