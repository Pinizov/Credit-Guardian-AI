"""Scraper for National Statistical Institute macro indicators (CPI, unemployment, wages).
Placeholder: Defines target endpoints and normalization approach.
"""
from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
from scrapers.base_scraper import BaseScraper
import csv
import io
import requests


class NSIMacroScraper(BaseScraper):
    name = "nsi_macro"
    base_url = "https://www.nsi.bg"

    # Example open data CSV endpoints (to verify actual codes)
    ENDPOINTS = {
        "cpi": "https://www.nsi.bg/opendata/cpi.csv",
        "unemployment_rate": "https://www.nsi.bg/opendata/unemployment.csv",
        "average_wage": "https://www.nsi.bg/opendata/wage.csv",
    }

    def _fetch_csv(self, url: str) -> list[dict[str, str]]:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return []
        text = resp.content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        return [row for row in reader]

    def scrape_all(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "scraped_at": datetime.utcnow().isoformat(),
            "indicators": [],
            "source": self.base_url,
        }
        for code, url in self.ENDPOINTS.items():
            rows = self._fetch_csv(url)
            for r in rows:
                # Expect columns like Date, Value
                date_val = r.get("Date") or r.get("date") or r.get("period")
                value_val = r.get("Value") or r.get("value")
                if not date_val or not value_val:
                    continue
                try:
                    val_num = float(value_val.replace(",", "."))
                except ValueError:
                    continue
                data["indicators"].append({
                    "indicator_code": code,
                    "date": date_val,
                    "value": val_num,
                })
        return data


if __name__ == "__main__":
    scraper = NSIMacroScraper()
    result = scraper.run("data/nsi_macro.json")
    print(f"Indicators collected: {len(result['indicators'])}")
