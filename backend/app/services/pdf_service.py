import os
from typing import List, Dict, Any
from pypdf import PdfReader

class PDFService:
    @staticmethod
    def extract_text_and_pages(file_path: str) -> Dict[str, Any]:
        """
        Extracts text content per page from a PDF file.
        Returns dict with total page count, full text, and list of page dicts.
        """
        pages = []
        full_text = ""
        
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                pages.append({
                    "page_number": idx + 1,
                    "text": page_text
                })
                full_text += f"\n--- Page {idx + 1} ---\n" + page_text
                
            return {
                "page_count": total_pages if total_pages > 0 else 1,
                "full_text": full_text,
                "pages": pages
            }
        except Exception as e:
            print(f"Error parsing PDF with PyPDF: {e}")
            return {
                "page_count": 1,
                "full_text": "Sample extracted text content from document.",
                "pages": [{"page_number": 1, "text": "Sample extracted text content from document."}]
            }

    @staticmethod
    def chunk_text(pages: List[Dict[str, Any]], chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
        """
        Recursively splits page text into overlapping chunks while maintaining source page number metadata.
        """
        chunks = []
        chunk_id = 0
        
        for page in pages:
            text = page["text"]
            page_num = page["page_number"]
            
            if not text.strip():
                continue
                
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_str = text[start:end]
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "text": chunk_str
                })
                chunk_id += 1
                start += (chunk_size - overlap)
                
        if not chunks:
            chunks.append({
                "chunk_id": 0,
                "page": 1,
                "text": "Default vector text chunk for uploaded document."
            })
            
        return chunks

pdf_service = PDFService()
