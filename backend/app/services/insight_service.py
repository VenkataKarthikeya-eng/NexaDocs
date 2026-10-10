import os
import re
import json
from typing import Dict, Any, List
import httpx
from app.core.config import settings

class InsightService:
    @staticmethod
    def _clean_summary_text(raw_text: str) -> str:
        """Strips JSON syntax, quotes, and markdown code fences from summary string."""
        if not raw_text:
            return ""
        s = raw_text.strip()
        if '"summary"' in s:
            match = re.search(r'"summary"\s*:\s*"([^"]+)"', s)
            if match:
                s = match.group(1)
        s = re.sub(r'^(?:```(?:json)?|"""(?:json)?|[\'"{}\[\]\s]+)+', '', s)
        s = re.sub(r'(?:```|"""|[\'"{}\[\]\s]+)+$', '', s)
        return s.strip()

    @staticmethod
    def generate_document_insights(filename: str, full_text: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates executive summary, key topics, extracted entities, and highlights.
        Leverages Google Gemini with multi-model fallback and factual extractive NLP fallback.
        Never fabricates entities or citations.
        """
        page_count = len(pages) if pages else 1
        clean_text = full_text.strip()

        # Build comprehensive sample representation across document pages (up to 8000 chars)
        sample_parts = []
        if pages:
            # Sample across beginning, middle, and end of document
            step = max(1, len(pages) // 5)
            for p in pages[::step]:
                p_text = p.get("text", "").strip()
                if p_text:
                    sample_parts.append(f"[Page {p.get('page_number', 1)}]: {p_text[:800]}")
            document_sample = "\n\n".join(sample_parts)[:7000]
        else:
            document_sample = clean_text[:7000]

        summary = ""
        topics = []
        entities = []
        highlights = []

        # 1. Attempt LLM-Powered Insight Extraction with Google Gemini
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
            candidate_models = [settings.GEMINI_MODEL]
            for m in getattr(settings, "GEMINI_FALLBACK_MODELS", ["gemini-3.5-flash", "gemini-flash-latest"]):
                if m not in candidate_models:
                    candidate_models.append(m)

            prompt = (
                f"You are NexaDocs AI, an enterprise document intelligence engine.\n"
                f"Analyze the following document '{filename}' ({page_count} pages) and extract structured insights.\n"
                f"Respond STRICTLY in valid JSON without any markdown formatting, backticks, or preamble.\n\n"
                f"Document Content:\n{document_sample}\n\n"
                f"JSON Schema:\n"
                f"{{\n"
                f'  "summary": "2-3 clear, executive sentences summarizing key findings, purpose, and content.",\n'
                f'  "topics": ["Topic1", "Topic2", "Topic3", "Topic4"],\n'
                f'  "entities": [\n'
                f'    {{"name": "Actual Entity Name", "type": "Organization|Technology|Metric|Regulatory", "detail": "Specific factual detail from text"}}\n'
                f"  ],\n"
                f'  "key_takeaways": [\n'
                f'    {{"page": 1, "text": "Specific key finding or milestone verified from the document."}}\n'
                f"  ]\n"
                f"}}"
            )

            for model_name in candidate_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800}
                }
                try:
                    with httpx.Client(timeout=25.0) as client:
                        res = client.post(url, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                raw_reply = "".join(p.get("text", "") for p in parts if "text" in p).strip()

                                # Extract JSON block
                                json_match = re.search(r'\{[\s\S]*\}', raw_reply)
                                if json_match:
                                    try:
                                        parsed = json.loads(json_match.group(0))
                                        if isinstance(parsed, dict):
                                            summary = InsightService._clean_summary_text(parsed.get("summary", ""))
                                            topics = parsed.get("topics", [])
                                            entities = parsed.get("entities", [])
                                            highlights = parsed.get("key_takeaways", [])
                                            if summary:
                                                break
                                    except Exception:
                                        pass
                        elif res.status_code in [503, 429, 404]:
                            print(f"[InsightService] Model {model_name} returned status {res.status_code}. Retrying fallback...")
                            continue
                except Exception as e:
                    print(f"[InsightService] Gemini extraction error on {model_name}: {e}")
                    continue

        # 2. Factual NLP Heuristic Fallback (if LLM unavailable or failed)
        if not summary:
            first_page_text = pages[0].get("text", "") if pages else clean_text
            lines = [l.strip() for l in first_page_text.split('\n') if len(l.strip()) > 30 and '@' not in l and 'http' not in l]
            if lines:
                summary = " ".join(lines[:2])
                if len(summary) > 300:
                    summary = summary[:300] + "..."
            else:
                summary = f"Indexed document {filename} ({page_count} pages) ready for verified vector question answering."

        # 3. Dynamic Topic Extraction from Genuine Frequent Words
        if not topics:
            words = re.findall(r'\b[A-Za-z]{4,}\b', clean_text)
            freq = {}
            stopwords = {
                "this", "that", "with", "from", "have", "were", "been", "which", "their", "there",
                "about", "would", "these", "other", "could", "first", "after", "should", "where"
            }
            for w in words:
                low = w.lower()
                if low not in stopwords:
                    freq[low] = freq.get(low, 0) + 1
            sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            top_words = [w[0].capitalize() for w in sorted_words[:5]]
            topics = top_words if top_words else ["Document Analysis", "General"]

        # 4. Factual Regex-Based Entity Extraction from Actual Document
        if not entities:
            real_entities = []
            real_entities.append({
                "name": filename,
                "type": "Source File",
                "detail": f"{page_count} Physical Page{'s' if page_count > 1 else ''}"
            })

            # Real monetary figures
            currencies = list(set(re.findall(r'\$[\d,.]+[MBKmbk]?', clean_text)))
            for curr in currencies[:2]:
                real_entities.append({"name": curr, "type": "Financial Metric", "detail": "Extracted figure"})

            # Real percentages
            percentages = list(set(re.findall(r'\b\d+(?:\.\d+)?%', clean_text)))
            for pct in percentages[:2]:
                real_entities.append({"name": pct, "type": "Performance Metric", "detail": "Extracted metric"})

            # Real capitalized proper nouns (Organizations/Products)
            proper_nouns = list(set(re.findall(r'\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?\b', clean_text)))
            meaningful_nouns = [n for n in proper_nouns if len(n) > 4 and n not in {"Document", "Report", "Page", "Section", "Table"}][:3]
            for n in meaningful_nouns:
                real_entities.append({"name": n, "type": "Entity", "detail": "Extracted from document"})

            entities = real_entities[:6]

        # 5. Factual Highlights with Exact Physical Page Numbers
        if not highlights:
            real_highlights = []
            for p in pages:
                p_num = p.get("page_number", 1)
                p_text = p.get("text", "").strip()
                if p_text:
                    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', p_text) if 35 < len(s.strip()) < 220]
                    clean_sentences = [
                        s for s in sentences
                        if '@' not in s and 'http' not in s and not re.search(r'\+?\d{10}', s)
                    ]
                    if clean_sentences:
                        real_highlights.append({
                            "page": p_num,
                            "text": clean_sentences[0]
                        })
                if len(real_highlights) >= 3:
                    break

            highlights = real_highlights

        return {
            "summary": summary,
            "topics": topics,
            "entities": entities,
            "key_takeaways": highlights
        }

insight_service = InsightService()
