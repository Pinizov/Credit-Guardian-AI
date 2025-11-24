import re
from typing import List

def normalize_text(text: str) -> str:
    """Normalize whitespace in text."""
    return re.sub(r'\s+', ' ', text).strip()

def extract_amounts(text: str) -> List[float]:
    """Extract monetary amounts from text."""
    amounts = []
    for m in re.finditer(r'(\d{2,9}[.,]\d{2})\s*лв', text):
        try:
            amounts.append(float(m.group(1).replace(',', '.')))
        except:
            pass
    return amounts

def extract_percentages(text: str) -> List[float]:
    """Extract percentages from text."""
    perc = []
    for m in re.finditer(r'(\d{1,3}[.,]\d{1,2})\s*%', text):
        try:
            perc.append(float(m.group(1).replace(',', '.')))
        except:
            pass
    return perc
