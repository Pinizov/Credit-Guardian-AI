"""Base scraper interface and utilities for Credit Guardian.
Provides a consistent pattern for network requests, parsing, transformation, and persistence.
"""
from __future__ import annotations
import time
import random
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import requests

logger = logging.getLogger("scrapers")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CreditGuardianBot/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "bg,en;q=0.9",
}


class BaseScraper(ABC):
    name: str = "base"
    base_url: str = ""
    delay: float = 1.5
    max_retries: int = 3
    timeout: int = 15

    def __init__(self, delay: float | None = None):
        self.delay = delay if delay is not None else self.delay
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _sleep(self):
        # jitter to reduce pattern detection
        time.sleep(self.delay + random.uniform(0, 0.4))

    def fetch_raw(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        last_err: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"{self.name}: Fetch {url} (attempt {attempt})")
                resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if resp.status_code >= 400:
                    raise RuntimeError(f"HTTP {resp.status_code}")
                return resp
            except Exception as e:
                last_err = e
                wait = attempt * 1.2
                logger.warning(f"{self.name}: Error {e}; retry in {wait:.1f}s")
                time.sleep(wait)
        logger.error(f"{self.name}: Failed after {self.max_retries} attempts: {last_err}")
        return None

    @abstractmethod
    def scrape_all(self) -> Dict[str, Any]:
        """Execute full scrape and return structured dict."""

    def save_to_json(self, data: Dict[str, Any], path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"{self.name}: Saved JSON -> {path}")
        except Exception as e:
            logger.error(f"{self.name}: Save failed {e}")

    def run(self, output_path: str | None = None) -> Dict[str, Any]:
        data = self.scrape_all()
        if output_path:
            self.save_to_json(data, output_path)
        return data
