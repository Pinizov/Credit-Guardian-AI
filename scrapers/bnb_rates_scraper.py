"""Scraper for Bulgarian National Bank base interest rate and reference indicators.
Placeholder implementation: outlines approach for extracting monthly base rate and deposit/credit stats.
"""
from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup  # type: ignore

class BNBRatesScraper(BaseScraper):
    name = "bnb_rates"
    base_url = "https://bnb.bg"

    RATE_PAGE = "/Statistics/StBaseInterestRate/index.htm"  # Example path; verify actual

    def scrape_all(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "scraped_at": datetime.utcnow().isoformat(),
            "base_interest_rates": [],  # list of {date, rate}
            "source": self.base_url,
        }
        url = self.base_url + self.RATE_PAGE
        resp = self.fetch_raw(url)
        if not resp:
            return data
        soup = BeautifulSoup(resp.content, "html.parser")
        # TODO: refine selectors once actual structure confirmed
        rows = soup.find_all("tr")
        for r in rows:
            cells = [c.get_text(strip=True) for c in r.find_all("td")]
            if len(cells) >= 2:
                date_text, rate_text = cells[0], cells[1]
                try:
                    rate_val = float(rate_text.replace(",", "."))
                except ValueError:
                    continue
                data["base_interest_rates"].append({
                    "date": date_text,
                    "rate": rate_val,
                })
        return data

if __name__ == "__main__":  # manual run
    scraper = BNBRatesScraper()
    result = scraper.run("data/bnb_rates.json")
    print(f"Collected {len(result['base_interest_rates'])} rate points")
