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
        """Extract financial data from contract text"""
        patterns = {
            "principal": r"(?:главница|principal|сума\s+(?:на\s+)?кредит)[:\s]*(\d+[\s\.,]?\d*)",
            "stated_apr": r"(?:ГПР|APR|годишен\s+процент)[:\s]*(\d+[.,]\d{1,2})\s*%",
            "total": r"(?:обща|total|дължима\s+сума)[:\s]*(\d+[\s\.,]?\d*)",
            "interest_rate": r"(?:лихва|interest\s+rate)[:\s]*(\d+[.,]\d{1,2})\s*%",
            "term_months": r"(?:срок|период)[:\s]*(\d+)\s*(?:месец|month)",
            # Specific fees
            "fee_fast_review": r"(?:бързо\s+разглеждане|fast\s+review)[:\s]*(\d+[.,]?\d*)",
            "fee_management": r"(?:управление|management)[:\s]*(\d+[.,]?\d*)",
            "fee_disbursement": r"(?:усвояване|disbursement)[:\s]*(\d+[.,]?\d*)",
            "monthly_payment": r"(?:месечна\s+вноска|monthly\s+payment)[:\s]*(\d+[.,]?\d*)",
        }
        out: Dict[str, float] = {}
        for k, pat in patterns.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                try:
                    # Clean number: remove spaces, replace comma with dot
                    num_str = m.group(1).replace(" ", "").replace(",", ".")
                    out[k] = float(num_str)
                except Exception:
                    pass
        return out
    
    @staticmethod
    def extract_dates(text: str) -> Dict[str, str]:
        """Extract dates from contract text"""
        patterns = {
            "contract_date": r"(?:дата\s+на\s+договор|contract\s+date)[:\s]*(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
            "maturity_date": r"(?:падеж|maturity)[:\s]*(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
            "first_payment_date": r"(?:първа\s+вноска|first\s+payment)[:\s]*(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        }
        dates: Dict[str, str] = {}
        for k, pat in patterns.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                date_str = m.group(1)
                # Normalize to YYYY-MM-DD
                try:
                    parts = re.split(r'[./]', date_str)
                    if len(parts) == 3:
                        day, month, year = parts
                        if len(year) == 2:
                            year = "20" + year
                        dates[k] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
        return dates
    
    @staticmethod
    def extract_creditor_info(text: str) -> Dict[str, str]:
        """Extract creditor information"""
        info: Dict[str, str] = {}
        
        # ЕИК/БУЛСТАТ
        eik_match = re.search(r"(?:ЕИК|БУЛСТАТ)[:\s]*(\d{9,13})", text, re.IGNORECASE)
        if eik_match:
            info["eik"] = eik_match.group(1)
        
        # Contract number
        contract_match = re.search(r"(?:договор|contract)\s*№?\s*([A-Z0-9\-/]+)", text, re.IGNORECASE)
        if contract_match:
            info["contract_number"] = contract_match.group(1)
        
        # Creditor name (often appears after КРЕДИТОДАТЕЛ or in header)
        creditor_match = re.search(r"(?:КРЕДИТОДАТЕЛ|creditor)[:\s]*([\w\s]+(?:АД|ООД|ЕООД))", text, re.IGNORECASE)
        if creditor_match:
            info["creditor"] = creditor_match.group(1).strip()
        
        return info
