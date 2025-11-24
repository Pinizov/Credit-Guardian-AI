"""Scraper for KZP (Consumer Protection Commission) complaints and decisions.
Placeholder: Extracts complaint summaries and decision metadata for risk signals.
"""
from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup  # type: ignore

class KZPComplaintsScraper(BaseScraper):
    name = "kzp_complaints"
    base_url = "https://kzp.bg"

    COMPLAINTS_PATH = "/complaints"  # Verify actual path
    DECISIONS_PATH = "/decisions"    # Verify actual path

    def _parse_listing(self, soup: BeautifulSoup, kind: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cards = soup.find_all("div", class_="card") or soup.find_all("article")
        for c in cards:
            title_el = c.find("h3") or c.find("h2") or c.find("a")
            date_el = c.find("time")
            url_el = c.find("a", href=True)
            title = title_el.get_text(strip=True) if title_el else None
            date_txt = date_el.get_text(strip=True) if date_el else None
            url = url_el["href"] if url_el else None
            if url and url.startswith("/"):
                url = self.base_url + url
            if title:
                items.append({
                    "type": kind,
                    "title": title,
                    "date": date_txt,
                    "url": url,
                })
        return items

    def scrape_all(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "scraped_at": datetime.utcnow().isoformat(),
            "complaints": [],
            "decisions": [],
            "source": self.base_url,
        }
        for path, key in [(self.COMPLAINTS_PATH, "complaints"), (self.DECISIONS_PATH, "decisions")]:
            url = self.base_url + path
            resp = self.fetch_raw(url)
            if not resp:
                continue
            soup = BeautifulSoup(resp.content, "html.parser")
            kind = key[:-1]
            parsed = self._parse_listing(soup, kind)
            data[key] = parsed
            self._sleep()
        return data

if __name__ == "__main__":
    scraper = KZPComplaintsScraper()
    result = scraper.run("data/kzp_data.json")
    print(f"Complaints: {len(result['complaints'])}; Decisions: {len(result['decisions'])}")
