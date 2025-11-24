import re
from typing import Dict
import PyPDF2
try:  # optional OCR path
    from pdf2image import convert_from_path  # type: ignore
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    convert_from_path = None
    pytesseract = None

class PDFProcessor:
    @staticmethod
    def extract_text(path: str) -> str:
        text = ""
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for p in reader.pages:
                    t = p.extract_text() or ""
                    text += t + "\n"
        except Exception:
            pass
        if len(text) < 300 and convert_from_path and pytesseract:  # attempt OCR
            try:
                images = convert_from_path(path)
                for img in images:
                    text += pytesseract.image_to_string(img, lang="bul")
            except Exception:
                pass
        return text

    @staticmethod
    def extract_numbers(text: str) -> Dict[str, float]:
        patterns = {
            "principal": r"(главница|principal)[^0-9]*(\d+[.,]\d{2})",
            "stated_apr": r"(ГПР|APR)[^0-9]*(\d+[.,]\d{1,2})%",
            "total": r"(общо дължима|total)[^0-9]*(\d+[.,]\d{2})",
        }
        out: Dict[str, float] = {}
        for k, pat in patterns.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                try:
                    out[k] = float(m.group(2).replace(",", "."))
                except Exception:
                    pass
        return out
