"""Scrapers package initialization.

Exports scraper classes for easier dynamic loading.
"""

from .apis_bg_scraper import ApisBgScraper  # noqa: F401
from .ciela_net_scraper import CielaNetScraper  # noqa: F401
from .lex_bg_scraper import LexBgScraper  # noqa: F401
from .base_scraper import BaseScraper  # noqa: F401
from .bnb_rates_scraper import BNBRatesScraper  # noqa: F401
from .nsi_macro_scraper import NSIMacroScraper  # noqa: F401
from .kzp_complaints_scraper import KZPComplaintsScraper  # noqa: F401
from .eur_lex_scraper import EURLexScraper  # noqa: F401

__all__ = [
    "ApisBgScraper",
    "CielaNetScraper",
    "LexBgScraper",
    "BaseScraper",
    "BNBRatesScraper",
    "NSIMacroScraper",
    "KZPComplaintsScraper",
    "EURLexScraper",
]
