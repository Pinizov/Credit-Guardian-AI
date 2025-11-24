"""Scraper for EUR-Lex consumer protection directives relevant to credit.
Placeholder: Fetches directive listing and extracts metadata for local indexing.
"""
from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup  # type: ignore


class EURLexScraper(BaseScraper):
    name = "eur_lex"
    base_url = "https://eur-lex.europa.eu"

    QUERY_PATH = "/search.html?type=advanced&qid=consumer-credit"  # Example placeholder

    def scrape_all(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "scraped_at": datetime.utcnow().isoformat(),
            "directives": [],
            "source": self.base_url,
        }
        url = self.base_url + self.QUERY_PATH
        resp = self.fetch_raw(url)
        if not resp:
            return data
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.find_all("a", href=True)
        for a in links:
            href = a["href"]
            title = a.get_text(strip=True)
            if "LEX" in href and title and len(title) > 15:
                full = href if href.startswith("http") else self.base_url + href
                data["directives"].append({
                    "title": title,
                    "url": full,
                })
        return data


if __name__ == "__main__":
    scraper = EURLexScraper()
    result = scraper.run("data/eur_lex.json")
    print(f"Directives collected: {len(result['directives'])}")
